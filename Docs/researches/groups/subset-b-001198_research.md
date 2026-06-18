# subset-b-001198 research

Grouped research for NI Comedi driver files under `sources/distributed-fs/ceph-client/drivers/comedi/drivers`. Each section preserves the source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_6527.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_6527.c

## Purpose
`ni_6527.c` is the Comedi PCI/PXI driver for National Instruments 6527 static isolated digital I/O boards. It exposes 24 digital input channels, 24 digital output channels, and an optional one-channel edge-detection command subdevice when an IRQ can be allocated. It uses PCI auto configuration and MMIO BAR1 register access.

## Important APIs, Types, And Functions
Key device metadata is `enum ni6527_boardid`, `struct ni6527_board`, and `ni6527_boards[]`, mapping PCI/PXI IDs to board names. `struct ni6527_private` caches the global deglitch `filter_interval` and per-channel `filter_enable` mask. The input filter path is `ni6527_di_insn_config()`, `ni6527_set_filter_interval()`, and `ni6527_set_filter_enable()`. DI reads are handled by `ni6527_di_insn_bits()`, which combines three byte registers into a 24-bit value. DO writes are handled by `ni6527_do_insn_bits()`, using `comedi_dio_update_state()` and hardware-inverted output writes.

The interrupt API consists of `ni6527_interrupt()`, `ni6527_intr_cmdtest()`, `ni6527_intr_cmd()`, `ni6527_intr_cancel()`, `ni6527_intr_insn_bits()`, and `ni6527_intr_insn_config()`. Edge masks are programmed by `ni6527_set_edge_detection()`, supporting both `INSN_CONFIG_CHANGE_NOTIFY` and `INSN_CONFIG_DIGITAL_TRIG`. Device lifecycle is `ni6527_auto_attach()`, `ni6527_detach()`, `ni6527_pci_probe()`, `ni6527_driver`, and `ni6527_pci_driver`.

## Control Flow
Probe calls `comedi_pci_auto_config()`, which invokes `ni6527_auto_attach()`. Attach validates the board context, allocates private state, enables PCI, maps BAR1, checks `NI6527_ID_REG == 0x27`, resets filters/edges/IRQs, optionally requests the PCI IRQ, and allocates three subdevices. Normal DI reads pull MMIO bytes directly. DO writes update only touched byte lanes and return Comedi logical state despite the inverted hardware encoding.

For edge notification, the user configures rising/falling masks, starts a command with fixed triggers (`TRIG_NOW`, `TRIG_OTHER`, `TRIG_FOLLOW`, `TRIG_COUNT`), and `ni6527_intr_cmd()` clears stale IRQs then enables edge IRQs. The ISR verifies the board asserted `NI6527_STATUS_IRQ`, pushes a dummy sample on edge status, dispatches Comedi events, and clears edge/overflow latches.

## State And Persistence
Persistent runtime state is only in kernel memory and board registers. `filter_interval` avoids redundant interval writes; `filter_enable` mirrors enabled filter channels. Output state is tracked by the Comedi subdevice `s->state`. Edge masks live in hardware rising/falling registers, not in private memory. All state is reset on attach and detach through `ni6527_reset()`.

## Dependencies And Integration Points
The file depends on `linux/comedi/comedi_pci.h`, Comedi subdevice helpers, PCI IDs, MMIO accessors, and IRQ registration. It integrates with the Comedi command engine through subdevice callbacks and with PCI hotplug through `module_comedi_pci_driver()`.

## Risks
The interrupt subdevice reports only a dummy sample, so users must read the DI subdevice to know the changed channel state. `INSN_CONFIG_CHANGE_NOTIFY` uses a 32-bit mask even though the device has 24 channels; higher bits are harmless but misleading. Output inversion is device-specific and easy to regress. Filter interval is global while enable is per-channel, so configuring different intervals on different channels will silently share the last nonzero interval.

## Test Signals
Useful tests include PCI ID match, BAR1 map and ID register validation, DI byte ordering, inverted DO byte writes for partial masks, filter interval rounding to 200 ns units, per-channel filter enable clearing, edge-mask preservation across partial updates, command validation trigger normalization, ISR `IRQ_NONE` for unrelated interrupts, and reset disabling filters/edges/IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_6527.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_65xx.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_65xx.c

## Purpose
`ni_65xx.c` supports a broad family of National Instruments PCI/PXI 65xx static digital I/O boards, including 6509, 6510-6519, 6520/6521, and 6528 variants. Depending on the board table, it exposes fixed DI, fixed DO, configurable DIO, and an optional interrupt change-notification subdevice.

## Important APIs, Types, And Functions
`struct ni_65xx_board` describes board names, port counts, and whether legacy output inversion is applicable. `ni_65xx_boards[]` is the central hardware capability table. `ni_65xx_legacy_invert_outputs` is a read-only module parameter that re-enables older Comedi output inversion behavior for selected 6513-6519 boards.

Port math uses `NI_65XX_PORT_TO_CHAN()`, `NI_65XX_CHAN_TO_PORT()`, and `NI_65XX_CHAN_TO_MASK()`. `ni_65xx_dio_insn_config()` handles deglitch filters and DIO direction. `ni_65xx_dio_insn_bits()` reads/writes port windows and applies `s->io_bits` inversion. Edge support is in `ni_65xx_update_edge_detection()`, `ni_65xx_disable_edge_detection()`, `ni_65xx_intr_insn_config()`, `ni_65xx_intr_cmdtest()`, `ni_65xx_intr_cmd()`, `ni_65xx_intr_cancel()`, and `ni_65xx_interrupt()`. `ni_65xx_mite_init()` manually configures the MITE window without taking a full MITE dependency. Attach/detach and PCI registration are `ni_65xx_auto_attach()`, `ni_65xx_detach()`, `ni_65xx_pci_probe()`, and `module_comedi_pci_driver()`.

## Control Flow
PCI probe passes a board index to Comedi auto attach. Attach enables PCI, opens the MITE BAR0 long enough to point the I/O window at BAR1, maps BAR1, clears edge/overflow state, disables interrupts, optionally requests a shared IRQ, logs the hardware ID, and allocates four subdevices. The first three subdevices are populated according to board capabilities: fixed DI starts at port 0, fixed DO starts after the DI ports, and configurable DIO starts at port 0. The fourth subdevice is always created as a one-channel DI status source and becomes command-capable only when an IRQ exists.

Runtime DIO operations iterate from the chanspec base channel to the last affected port, shift user masks into the hardware port window, update outputs, and read back actual port state. Filter config rounds nanosecond values into 200 ns hardware units, clamps to 20 bits, and writes a global filter interval plus per-port enable bits. Edge commands program rising/falling enable registers and use a dummy sample to wake Comedi async consumers on change events.

## State And Persistence
The board table is static. Direction state for configurable DIO is in hardware `IO_SEL` registers. Output inversion is represented through `s->io_bits`; output values are initialized to logical zero. Filter enable bits are read-modify-written from hardware rather than mirrored in a private struct. Edge masks live in hardware registers. The driver does not allocate private state because it relies on board metadata and subdevice fields.

## Dependencies And Integration Points
The driver depends on Comedi PCI helpers, Linux IRQ handling, BAR MMIO accessors, and Comedi DIO/command callbacks. Its MITE setup is a local minimal register write to `MITE_IODWBSR`; unlike NI MIO/TIO drivers, it does not use the full MITE DMA layer.

## Risks
The file comments warn the interrupt subdevice is probably broken for most boards except possibly 6514. Edge notification covers only configured masks and reports no changed-port payload. Filter interval is board-global, so multiple channels cannot hold independent intervals. Legacy inversion is optional and only applied when both module parameter and board metadata opt in; changing that behavior can break old user space. DIO direction writes apply to whole ports, while Comedi config is per-channel, so mixed direction expectations inside one 8-bit port are unsafe.

## Test Signals
Tests should cover each board table entry producing the correct subdevice layout and channel counts, MITE window setup failure paths, fixed DI/DO port offsets, configurable DIO direction query, output inversion under the module parameter, filter rounding/clamping, edge-mask updates across channel ranges 0-95, interrupt rejection for unrelated status bits, and detach disabling interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_65xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_660x.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_660x.c

## Purpose
`ni_660x.c` is the Comedi PCI/PXI driver for NI 660x and 6624 counter/timer boards. It provides a 40-channel PFI/DIO subdevice plus up to eight NI-TIO general-purpose counter subdevices. It supports buffered input commands through MITE DMA, counter routing through NI route tables, and global signal-route device configuration calls.

## Important APIs, Types, And Functions
The driver extends `enum ni_gpct_register` with NI-660x-specific registers and maps each register to offset/width through `struct ni_660x_register_data ni_660x_reg_data[]`. Board capabilities live in `struct ni_660x_board` and `ni_660x_boards[]`, primarily the number of TIO chips. `struct ni_660x_private` owns the MITE handle, NI-GPCT device, per-counter MITE rings, locks, per-chip DMA config shadows, PFI route/direction state, and `struct ni_route_tables`.

Register access is `ni_660x_read()`/`ni_660x_write()`, with NI-TIO bridge callbacks `ni_660x_gpct_read()` and `ni_660x_gpct_write()`. DMA management is `ni_660x_request_mite_channel()`, `ni_660x_release_mite_channel()`, `ni_660x_cmd()`, `ni_660x_cancel()`, `ni_660x_input_poll()`, and `ni_660x_buf_change()`. PFI/DIO callbacks are `ni_660x_dio_insn_bits()` and `ni_660x_dio_insn_config()`. Routing support is `_ni_get_valid_routes()`, `test_route()`, `connect_route()`, `disconnect_route()`, and `ni_global_insn_config()`. Lifecycle is `ni_660x_auto_attach()` and `ni_660x_detach()`.

## Control Flow
Auto attach validates the board context, enables PCI, allocates private state and locks, attaches MITE with window 1, allocates one MITE ring per possible counter, initializes DMA and IO config registers, loads route tables, constructs an NI-GPCT device, and creates `2 + NI660X_MAX_COUNTERS` subdevices. Subdevice 0 is an unused legacy counter placeholder. Subdevice 1 is the PFI/DIO view. Remaining subdevices are one Comedi counter per real NI-TIO counter; unused slots are marked unused.

Buffered counter input starts through a counter subdevice command. `ni_660x_cmd()` reserves a MITE DMA channel under lock, maps it to the counter in hardware, acknowledges stale TIO status, and delegates command programming to `ni_tio_cmd()`. Cancellation reverses that by cancelling NI-TIO and releasing the MITE channel. Interrupts iterate over all counter subdevices under `interrupt_lock`, call `ni_tio_handle_interrupt()`, and dispatch Comedi events. Polling also takes `interrupt_lock` before syncing DMA.

PFI direction and routing are decoupled: `io_cfg[]` remembers the desired source, while `io_dir` controls whether a pin actively drives or is high impedance. Route connection validates against route tables and refuses to overwrite a busy destination.

## State And Persistence
Runtime state is entirely volatile: DMA rings/channels, NI-TIO counter objects, shadow DMA config registers, PFI direction bitmap, PFI source array, and route tables. Hardware is initialized to high impedance PFI inputs, default DIO/counter route sources, DMA disabled, and global interrupts enabled after IRQ registration. Detach disables global interrupts, frees IRQ, destroys NI-GPCT state, frees rings, detaches MITE, unmaps MMIO, and disables PCI.

## Dependencies And Integration Points
This file integrates with the Comedi PCI layer, `mite.h` DMA infrastructure, `ni_tio.h` counter engine, and `ni_routes.h` signal naming/routing helpers. It exposes device-level route config through `dev->insn_device_config` and `dev->get_valid_routes` only when route tables are available.

## Risks
The route layer explicitly leaves RTSI output routing unimplemented, so route tests may succeed only for PFI and counter destinations. Buffered output commands are documented as unsupported. PFI channels 32-39 are not usable as generic DIO despite being in the DIO subdevice. The interrupt handler returns `IRQ_HANDLED` after scanning counters without first checking a global status bit, which is normal for shared TIO handling here but can obscure stray IRQ analysis. DMA channel reservation/release and poll/interrupt locking are critical; missed locking can corrupt MITE state or async buffers.

## Test Signals
Test signals include board-specific counter counts, register offset/width access, MITE attach/ring allocation cleanup on failure, PFI default direction/routing, DIO writes only affecting first 32 channels, `INSN_CONFIG_SET_ROUTING` validation, route connect returning `-EBUSY` for occupied destinations and `-EALREADY` for existing routes, counter command DMA channel assignment/reset bits, cancel releasing MITE channels, and detach releasing every allocated resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_660x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_670x.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_670x.c

## Purpose
`ni_670x.c` supports NI PCI/PXI 6703/6704 analog output boards. It exposes a simple analog-output instruction interface and one 8-channel digital I/O subdevice. It does not support Comedi streaming commands.

## Important APIs, Types, And Functions
Board metadata is in `enum ni_670x_boardid`, `struct ni_670x_board`, and `ni_670x_boards[]`, where 6703 has 16 AO channels and 6704 variants have 32. `ni_670x_ao_insn_write()` writes AO channel select and value registers and maintains Comedi readback. `ni_670x_dio_insn_bits()` and `ni_670x_dio_insn_config()` implement simple DIO state and direction through port 0 data/direction registers. `ni_670x_mite_init()` manually sets the MITE I/O window. `ni_670x_auto_attach()` and `ni_670x_detach()` handle PCI setup and teardown.

## Control Flow
PCI probe invokes Comedi auto configuration with a board index. Attach enables PCI, allocates private storage, initializes the MITE data window from BAR0 to BAR1, maps BAR1, and allocates two subdevices. AO setup chooses either a single bipolar range table for 16-channel boards or a per-channel range list for 32-channel boards: channels 0-15 are bipolar voltage, channels 16-31 are 0-20 mA. DIO setup installs generic Comedi DIO config and bits callbacks. Finally, misc and AO control registers are initialized.

AO writes map the Comedi channel to hardware channel encoding using `((chan & 15) << 1) | ((chan & 16) >> 4)`, then write the data value. DIO writes update `s->state`, write port 0 data if the mask changed, and read back port 0 data.

## State And Persistence
AO readback is maintained by `comedi_alloc_subdev_readback()`. DIO state and direction are stored in the Comedi subdevice and mirrored to hardware registers. The private struct currently contains unused fields, so most persistent runtime state is in subdevices and hardware. The dynamically allocated per-channel range table for 32-channel boards is freed in detach.

## Dependencies And Integration Points
The driver depends on Comedi PCI helpers, MMIO accessors, `kmalloc_objs()`/`kfree()`, and standard Comedi AO/DIO callback contracts. It repeats local MITE window setup rather than using full MITE abstractions.

## Risks
The driver trusts instruction channel/range validation from Comedi core and does not explicitly poll AO status. `ni_670x_private` fields are unused, which may hide stale design intent. Detach calls `comedi_pci_detach()` before freeing the range-table list; because the list is normal heap memory rather than PCI memory this is acceptable, but cleanup ordering should be preserved carefully. Current-output channels on 6704 depend on the correct per-channel range list.

## Test Signals
Tests should confirm PCI IDs map to 16/32 channel layouts, MITE setup writes BAR1 physical address with window enable, AO channel encoding for channels 0, 15, 16, and 31, readback update after repeated writes, 6704 range-table allocation/failure handling, DIO direction writes to `DIO_PORT0_DIR_OFFSET`, and detach freeing the optional range table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_670x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_a2150.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_a2150.c

## Purpose
`ni_at_a2150.c` is a legacy ISA Comedi driver for NI AT-A2150C/S analog input boards. It supports single-sample reads and, when valid IRQ and DMA options are supplied, asynchronous timed acquisition using ISA DMA.

## Important APIs, Types, And Functions
`struct a2150_board` describes clock periods and maximum AI speed for the C and S variants. `struct a2150_private` stores ISA DMA state, remaining sample count, IRQ/DMA register shadow bits, and configuration register shadow bits. `a2150_probe()` identifies the board from `STATUS_REG` ID bits. `a2150_get_timing()` rounds requested scan periods to board clock/divisor combinations and updates config bits. `a2150_set_chanlist()` and `a2150_ai_check_chanlist()` enforce hardware channel grouping constraints.

Command validation and execution are in `a2150_ai_cmdtest()` and `a2150_ai_cmd()`. Interrupt-driven DMA completion is handled by `a2150_interrupt()`. Single reads use `a2150_ai_rinsn()` and `a2150_ai_eoc()`. Resource helpers are `a2150_alloc_irq_and_dma()`, `a2150_free_dma()`, `a2150_attach()`, `a2150_detach()`, and `a2150_cancel()`.

## Control Flow
Attach allocates private state, requests the ISA I/O region, probes board ID, optionally allocates IRQ plus one ISA DMA buffer, allocates an 8254 pacer, creates one AI subdevice, powers and calibrates the ADC path, waits for offset calibration to finish, and enables analog input channels. If no IRQ/DMA is available, the AI subdevice remains instruction-only.

For a command, `a2150_ai_cmd()` cancels/clears FIFO state, programs channel grouping and AC/DC coupling, rounds timing, writes config bits, calculates remaining samples, disables and programs ISA DMA, clears pending terminal-count interrupt, enables board DMA/interrupts, loads counter 2 for the 72-period settling delay, configures software or external trigger bits, and starts acquisition for `TRIG_NOW`. The ISR validates interrupt status and DMA terminal count, disables DMA to get residue, computes received samples and the next transfer size, converts two's-complement ADC samples to unsigned, writes them to the Comedi buffer, reprograms DMA if needed, handles EOA, dispatches events, and clears the terminal count interrupt.

## State And Persistence
State lives in `devpriv->config_bits`, `devpriv->irq_dma_bits`, the ISA DMA descriptor, and `devpriv->count`. The 8254 pacer and board registers hold timing/trigger state. Detach powers down analog/digital circuitry, frees DMA, and releases legacy resources.

## Dependencies And Integration Points
The driver depends on ISA I/O port access, `comedi_isadma`, `comedi_8254`, Linux IRQ APIs, Comedi command validation helpers, and Comedi async buffers. It exposes only one AI subdevice.

## Risks
Command path requires both IRQ and DMA; a misconfigured user gets no async capability. `a2150_ai_cmd()` reads `cmd->chanlist[2]` while setting AC coupling for channels 2/3, which is risky for one- or two-channel commands and relies on surrounding assumptions. DMA residue handling is subtle for external stop triggers. Timing rounding mutates both requested timing and hardware shadow bits. The code returns `-1` in several paths rather than specific errno values.

## Test Signals
Useful tests include board ID probe for C/S, invalid IRQ/DMA rejection, calibration timeout behavior, timing rounding across all master clocks/divisors and round modes, chanlist validation for 1/2/4 channels, instruction read discarding 36 filter-delay samples, command setup for external versus software start, DMA transfer sizing, residue handling, EOA on count exhaustion, overflow/error event generation, cancel disabling board and host DMA, and detach powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_a2150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_ao.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_ao.c

## Purpose
`ni_at_ao.c` is the legacy ISA Comedi driver for NI AT-AO-6 and AT-AO-10 analog output boards. It provides direct AO writes, 8-bit DIO, and internal calibration DAC access. IRQ and DMA configuration options are documented but unused.

## Important APIs, Types, And Functions
`struct atao_board` defines board name and AO channel count. `struct atao_private` shadows command registers `cfg1` and `cfg3` and has a `caldac` array for calibration readback intent. `atao_select_reg_group()` toggles the alternate register group bit. `atao_ao_insn_write()` writes AO samples after Comedi offset munging. `atao_dio_insn_bits()` and `atao_dio_insn_config()` implement 8-bit DIO with nibble-granular direction. `atao_calib_insn_write()` serializes channel/value data into three DAC8800 TrimDACs. `atao_reset()` applies the documented board reset sequence. `atao_attach()` creates all subdevices.

## Control Flow
Legacy attach requests a 0x20-byte I/O region, allocates private data, allocates an 8254 pacer, and creates four subdevices: AO, DIO, calibration, and an unused EEPROM placeholder. AO channel 0 requires register group 2 access, so writes to channel 0 temporarily select group 2 and restore group 1 afterward. DIO config maps channel 0-3 and 4-7 to separate output-enable bits in `CFG3`. Calibration writes clock an 11-bit channel/value bitstring MSB first, then strobe the target caldac.

Reset clears command registers, configures counter outputs high, puts caldac control into NOP, clears the FIFO, selects group 2 to clear interrupt/DMA flags, and returns to group 1.

## State And Persistence
Persistent runtime state is the command-register shadows in `atao_private`, AO and calibration readback arrays, and DIO subdevice state/io bits. Hardware outputs remain programmed until reset or subsequent writes. No streaming state is present.

## Dependencies And Integration Points
The driver uses legacy Comedi attachment, ISA port I/O, Comedi 8254 helper allocation, Comedi DIO helpers, and `module_comedi_driver()`. It is selected by board name through the `comedi_driver` board table rather than PCI/PCMCIA auto discovery.

## Risks
The EEPROM subdevice is unused despite calibration values being factory-stored there; calibration persistence must be handled by user tooling or external mechanisms. DIO direction is configured per nibble, not per channel. AO range is selected solely from user option `[3]`, reflecting hardware jumpers; incorrect configuration misrepresents output voltage. Register group switching around channel 0 is a fragile hardware quirk.

## Test Signals
Tests should verify board-name selection for 6/10 AO channels, I/O region validation, AO offset-munged writes and channel 0 group switching, AO readback, DIO nibble direction mapping to `CFG3`, caldac serial bit order and strobe, reset register sequence, pacer allocation failure, and detach through `comedi_legacy_detach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_at_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio.c

## Purpose
`ni_atmio.c` is the ISA/ISA-PnP front end for NI AT-MIO E-series boards. It defines board capability tables and attachment/probing logic, then includes and delegates most hardware operation to the shared `ni_mio_common.c` E-series implementation.

## Important APIs, Types, And Functions
The file defines `range_ni_E_ao_ext`, `ni_boards[]` entries of `struct ni_board_struct`, and the ISA IRQ-to-STC interrupt pin map `ni_irqpin[]`. It includes `"ni_stc.h"` and then `"ni_mio_common.c"`, making shared NI MIO functions and types part of this translation unit. ISA-PnP support uses `device_ids[]` and `ni_isapnp_find_board()`. `ni_atmio_probe()` reads EEPROM address 511 through `ni_read_eeprom()` to match `device_id`. `ni_atmio_attach()` performs private allocation, optional PnP discovery, I/O region request, board probe, IRQ request, and `ni_E_init()`. `ni_atmio_detach()` tears down shared MIO and PnP resources.

## Control Flow
When configured without an I/O base, attach scans known ISA-PnP IDs, activates the first valid device, extracts I/O base and IRQ, and binds the Comedi hardware device pointer to the PnP device. Otherwise it uses explicit config options. After requesting a 0x20-byte I/O region, the driver probes EEPROM device ID to choose a board descriptor. If an IRQ is configured, it validates the IRQ against `ni_irqpin[]`, requests it with `ni_E_interrupt`, and stores it. Shared NI E-series initialization then builds the actual AI/AO/DIO/counter/calibration subdevices according to board capabilities.

## State And Persistence
This file contributes static board metadata and no private state of its own beyond what `ni_alloc_private()` and `ni_mio_common.c` allocate. PnP attachment state is stored in `dev->hw_dev`; detach converts it back to `struct pnp_dev` and detaches it after common cleanup.

## Dependencies And Integration Points
Dependencies include Linux ISA-PnP, Comedi legacy attachment, optional 8255 support, `ni_stc.h`, and the included `ni_mio_common.c`. It is tightly coupled to shared NI MIO symbols such as `ni_alloc_private()`, `ni_read_eeprom()`, `ni_E_interrupt()`, `ni_E_init()`, and `mio_common_detach()`.

## Risks
Including a `.c` file is intentional in this driver family but creates tight compile-time coupling and can hide symbol ownership. Several board ISA-PnP IDs are unknown and cannot be autodetected. EEPROM probe failures produce user-facing errors but no fallback board selection. IRQ validation depends on the static `ni_irqpin[]` map. Calibration quality is explicitly poor at boot unless user-space calibration is applied.

## Test Signals
Tests should exercise explicit and auto PnP attach paths, PnP activation failure cleanup, I/O region bounds, EEPROM device ID matching and unknown-device errors, IRQ validation for accepted/rejected ISA IRQs, `ni_E_init()` invocation with correct IRQ pin, shared detach plus PnP detach, and board table correctness for AI/AO channels, FIFO depths, gain tables, caldac types, 8255 presence, and speed limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio16d.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio16d.c

## Purpose
`ni_atmio16d.c` is a legacy ISA Comedi driver for NI AT-MIO-16 and AT-MIO-16D boards. It exposes analog input, analog output, onboard 8-bit DIO, and optionally an 8255 DIO subdevice for the D variant. It includes an experimental interrupt-driven AI command path.

## Important APIs, Types, And Functions
Register and bit definitions cover command/status registers, mux/gain programming, AM9513A counters, DACs, onboard DIO, RTSI, and DIO-24 8255 offsets. `struct atmio16_board_t` distinguishes plain and D boards. `struct atmio16d_private` records user-configured ADC/DAC mux/range/coding/reference settings, AO range table pointers, and command-register shadows.

`reset_atmio16d()` and `reset_counters()` initialize hardware. `atmio16d_ai_insn_read()` performs polled single conversions. `atmio16d_ai_cmdtest()` and `atmio16d_ai_cmd()` validate and program timed acquisition. `atmio16d_interrupt()` reads one FIFO sample and dispatches events. AO and DIO callbacks are `atmio16d_ao_insn_write()`, `atmio16d_dio_insn_bits()`, and `atmio16d_dio_insn_config()`. Lifecycle is `atmio16d_attach()` and `atmio16d_detach()`.

## Control Flow
Attach requests the ISA I/O region, allocates four subdevices and private state, resets the board, optionally requests the AI IRQ, stores configuration options for ADC mux/range and DAC range/reference/coding, and initializes AI, AO, DIO, and optional 8255 subdevices. AI instruction reads program mux/gain, start conversion, wait for `STAT_AD_CONVAVAIL`, read FIFO, and apply two's-complement adjustment if configured.

The command path resets counters, enables or disables scan mode from chanlist length, programs the mux/gain scan list, chooses AM9513 base clocks for convert and scan intervals, programs sample count using counter 4 alone or counters 4/5 as a 32-bit count, clears FIFO and interrupts, enables DAQ and conversion interrupts, and starts acquisition. The ISR currently reads a single sample per interrupt and reports events.

## State And Persistence
The private command-register shadows are important because DIO, scan, and command setup modify the same registers across code paths. User options define persistent interpretation of ADC and DAC coding/ranges for the life of the attachment. AO readback is allocated by Comedi. Reset zeroes outputs, initializes timers, clears FIFOs, and selects straight binary ADC coding.

## Dependencies And Integration Points
The driver depends on legacy ISA port I/O, Linux IRQ APIs, Comedi 8255 helper, Comedi command validation, and standard Comedi AI/AO/DIO subdevices. It does not implement DMA despite configuration options documenting DMA channels.

## Risks
The command interface is explicitly described as experimental. The ISR reads only one sample and does not inspect status/error bits, which risks buffer underflow/overflow behavior under real hardware rates. DMA options are documented but unused. Counter programming is dense and hardware-specific. DIO direction is grouped by nibble. Some user options, such as DAC external reference, are stored but not visibly programmed in this file.

## Test Signals
Tests should cover both board names and 8255 presence, option parsing for mux/range/coding, reset register writes, AI range table selection, polled AI timeout/overflow behavior, AO two's-complement munging, DIO nibble direction command-register bits, command trigger validation, AM9513 timer selection at threshold periods, 16-bit versus 32-bit sample count programming, IRQ attach/no-IRQ command availability, and detach reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_atmio16d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_700.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_700.c

## Purpose
`ni_daq_700.c` is a PCMCIA Comedi driver for the NI DAQCard-700. It exposes a fixed 16-channel digital I/O subdevice and a 16-channel single-ended or 8-channel differential analog input subdevice with three bipolar ranges. The IRQ assigned by PCMCIA is not used.

## Important APIs, Types, And Functions
The file defines DAQCard-700 register offsets and `range_daq700_ai`. `daq700_dio_insn_bits()` handles lower-byte outputs and upper-byte inputs. `daq700_dio_insn_config()` forces the fixed output/input split through `s->io_bits = 0x00ff`. `daq700_ai_eoc()` interprets status registers for data-ready, overflow, and busy states. `daq700_ai_rinsn()` configures range/reference/channel, triggers conversions through counter mode writes, clears the FIFO, waits for completion, and converts bipolar offset-binary samples. `daq700_ai_config()` initializes the board. PCMCIA lifecycle is `daq700_auto_attach()`, `daq700_cs_attach()`, and the PCMCIA/Comedi driver tables.

## Control Flow
PCMCIA probe calls `comedi_pcmcia_auto_config()`. Auto attach requests automatic I/O resource assignment, enables the card, records the I/O base, and allocates two subdevices. DIO is fixed: channels 0-7 write to `DIO_W`, channels 8-15 read from `DIO_R`. AI setup writes default command registers to disable scanning, select channel 0, set +/-10 V single-ended mode, configure the onboard counter mode, clear interrupts, and drain FIFO junk.

For each instruction sample, AI read sets differential mode and range bits, selects the mux with scan disabled, delays 2 microseconds for settling, starts conversion by toggling command/counter registers, clears FIFO and junk data, polls `daq700_ai_eoc()`, reads the 12-bit FIFO sample, and XORs bit 11 to convert to Comedi unsigned encoding.

## State And Persistence
DIO output state is kept in `s->state`; direction is fixed by `s->io_bits`. AI has no private state and reprograms mode/channel/range for each instruction. Hardware is initialized once at attach and then reconfigured per AI instruction.

## Dependencies And Integration Points
The file depends on Comedi PCMCIA helpers, Linux delay functions, ISA-style port I/O, and Comedi timeout logic. It registers a PCMCIA manufacturer/card ID pair for auto attach.

## Risks
The driver uses polled AI only, so high-rate acquisition is unsupported. The conversion sequence relies on specific counter-mode writes and a fixed 2 us mux-settling delay. `daq700_ai_eoc()` returns overflow if status register 2 has either low bit set; hardware status interpretation should not be changed casually. DIO direction requests are accepted through Comedi config but then forced back to fixed hardware direction.

## Test Signals
Test signals include PCMCIA resource enable failure, fixed DIO split and readback composition, rejecting attempts to make fixed input channels outputs via the final `io_bits`, AI range hardware encoding where user range 1/2 maps to hardware 2/3, differential mode bit selection, mux settle delay presence, FIFO clear/junk read sequence, timeout paths for busy/no data/overflow, and offset-binary conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_dio24.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_dio24.c

## Purpose
`ni_daq_dio24.c` is a thin PCMCIA wrapper for the NI DAQ-Card DIO-24. Its role is to enable the PCMCIA device and expose the card's 8255 digital I/O through the generic Comedi 8255 subdevice helper.

## Important APIs, Types, And Functions
`dio24_auto_attach()` is the only substantial attach function. It enables automatic PCMCIA I/O assignment, enables the card, records the I/O base, allocates one subdevice, and calls `subdev_8255_io_init()`. `driver_dio24`, `dio24_cs_attach()`, `dio24_cs_ids[]`, and `dio24_cs_driver` register the Comedi and PCMCIA drivers.

## Control Flow
PCMCIA matching on manufacturer/card ID `0x010b/0x475c` invokes `dio24_cs_attach()`, which delegates to `comedi_pcmcia_auto_config()`. Comedi auto attach enables the PCMCIA I/O resource and delegates all DIO operation to the 8255 helper at offset 0. Remove calls `comedi_pcmcia_auto_unconfig()`, and Comedi detach disables the PCMCIA device.

## State And Persistence
The file has no private device state. DIO direction and output state are handled inside the generic 8255 subdevice created by `subdev_8255_io_init()`. Hardware state lasts until changed by user operations or card removal.

## Dependencies And Integration Points
Dependencies are `linux/comedi/comedi_pcmcia.h`, `linux/comedi/comedi_8255.h`, PCMCIA ID matching, and Comedi PCMCIA registration macros. The integration point is deliberately narrow: resource setup here, DIO behavior in the shared 8255 driver.

## Risks
Any board-specific DIO quirks beyond a standard 8255 are not represented. There is no IRQ, DMA, or analog support. Because this is a wrapper, regressions are most likely in resource enable/disable ordering or incorrect I/O base handoff to the 8255 helper.

## Test Signals
Tests should confirm PCMCIA ID matching, auto I/O assignment, `dev->iobase` from resource 0, one subdevice allocated, successful and failing `subdev_8255_io_init()` paths, and PCMCIA disable on detach/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_daq_dio24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.c

## Purpose
`ni_labpc.c` is the ISA bus front end for NI Lab-PC, Lab-PC-1200, Lab-PC-1200AI, and Lab-PC+ boards. It supplies board metadata, legacy attach/detach, I/O region acquisition, and optional ISA DMA initialization, while delegating most hardware behavior to `ni_labpc_common.c`.

## Important APIs, Types, And Functions
`labpc_boards[]` is the board table of `struct labpc_boardinfo`, declaring AI speed, scan-up capability, AO presence, and Lab-PC-1200 register support. `labpc_attach()` requests the ISA I/O range, calls `labpc_common_attach(dev, irq, 0)`, and initializes ISA DMA through `labpc_init_dma_chan()` only when an IRQ was successfully obtained. `labpc_detach()` frees ISA DMA, calls common detach, and releases legacy resources. `labpc_driver` registers board-name based Comedi legacy attachment.

## Control Flow
User-space legacy configuration selects one of the board names and passes I/O base, optional IRQ, and optional DMA channel. Attach reserves 0x20 I/O bytes, invokes the common Lab-PC attach path to allocate private state, register the IRQ, set up timers/subdevices/calibration/EEPROM, and then enables DMA support if both common attach recorded an IRQ and the DMA channel is valid. Detach reverses the optional DMA and common resources before generic legacy detach.

## State And Persistence
This file owns no unique private state. It relies on `struct labpc_private` allocated in common code, and optional `devpriv->dma` allocated by `ni_labpc_isadma.c`. Static board metadata controls persistent capabilities for the attachment.

## Dependencies And Integration Points
It depends on Comedi legacy device configuration, ISA I/O port reservation, `ni_labpc.h` for shared board/private definitions, and `ni_labpc_isadma.h` for optional DMA helpers. It integrates with `labpc_common_attach()` and `labpc_common_detach()`.

## Risks
DMA is initialized only after common attach and only if IRQ registration succeeded, so DMA cannot be used for polled-only devices. If the optional DMA Kconfig helper is disabled, the inline stubs make DMA options silently ineffective. Board metadata drives common behavior; incorrect `is_labpc1200`, `has_ao`, or `ai_scan_up` flags change subdevice layout and command validation.

## Test Signals
Tests should cover all three board table entries, I/O region request bounds, attach without IRQ, attach with IRQ and invalid/valid DMA channel, DMA helper stubs under disabled config, common attach failure propagation, detach ordering, and board flags reflected in common subdevice layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.h

## Purpose
`ni_labpc.h` is the shared interface for ISA, PCI, PCMCIA, common, and ISA-DMA Lab-PC driver pieces. It defines board capabilities, private runtime state, transfer modes, and the common attach/detach entry points.

## Important APIs, Types, And Functions
`enum transfer_type` distinguishes FIFO-not-empty, FIFO-half-full, and ISA-DMA acquisition transfers. `struct labpc_boardinfo` describes board name, maximum AI speed in nanoseconds, scan-up support, AO presence, and Lab-PC-1200 register availability. `struct labpc_private` stores optional ISA DMA, an 8254 counter helper, remaining sample count, command-register shadows `cmd1` through `cmd6`, last status-register reads, current transfer mode, and function pointers for byte access. The exported declarations are `labpc_common_attach()` and `labpc_common_detach()`.

## Control Flow
Bus-specific files populate `dev->board_ptr` with a `struct labpc_boardinfo`, establish either `dev->iobase` or `dev->mmio`, and call `labpc_common_attach()`. Common code fills `struct labpc_private`, installs I/O or MMIO byte-access callbacks, creates subdevices, and uses the shared fields during commands, interrupts, calibration, and EEPROM operations.

## State And Persistence
The header defines the state contract but does not allocate state. The command-register shadows persist across operations to prevent unrelated bitfields from being lost during DIO/AO/AI changes. The read/write function pointers persist for the attachment lifetime and abstract ISA/PCMCIA port I/O from PCI MMIO.

## Dependencies And Integration Points
The types reference `struct comedi_isadma`, `struct comedi_8254`, and Comedi device/subdevice types. It is included by `ni_labpc.c`, `ni_labpc_common.c`, `ni_labpc_cs.c`, `ni_labpc_isadma.c`, and `ni_labpc_pci.c`.

## Risks
Because this header is the ABI between split compilation units, any field layout or semantic change must be coordinated across common and bus-specific drivers. The access function pointers must be initialized before any register helper is used. Command-register shadows can become inconsistent if a code path writes hardware directly without updating the corresponding shadow.

## Test Signals
Test signals are compile/link level: every bus wrapper should build against the declarations, Kconfig combinations with and without ISA DMA should compile, `labpc_private` fields should be initialized before use in common attach, and static analysis should verify no direct command-register writes bypass the intended shadows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_common.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_common.c

## Purpose
`ni_labpc_common.c` contains the shared Lab-PC implementation for ISA `ni_labpc`, PCI `ni_labpc_pci`, and PCMCIA `ni_labpc_cs`. It implements AI instruction reads, AI command validation/execution, interrupt handling, AO writes, 8255 DIO setup, calibration DAC access, EEPROM access, and common resource initialization.

## Important APIs, Types, And Functions
`enum scan_mode` classifies single-channel, interval single-channel, multi-channel up, and multi-channel down scans. Range tables define Lab-PC+ AI, Lab-PC-1200 AI, and AO ranges. Access adapters `labpc_inb()`/`labpc_outb()` and `labpc_readb()`/`labpc_writeb()` let common code target I/O ports or MMIO.

AI helpers include `labpc_cancel()`, `labpc_ai_set_chan_and_gain()`, `labpc_setup_cmd6_reg()`, `labpc_read_adc_fifo()`, `labpc_clear_adc_fifo()`, `labpc_ai_insn_read()`, timing helpers around `labpc_adc_timing()`, `labpc_ai_scan_mode()`, `labpc_ai_check_chanlist()`, `labpc_ai_cmdtest()`, and `labpc_ai_cmd()`. Data movement is handled by `labpc_drain_fifo()`, `labpc_drain_dregs()`, and `labpc_interrupt()`, with ISA DMA delegated to `labpc_setup_dma()`, `labpc_drain_dma()`, and `labpc_handle_dma_status()`. AO/calibration/EEPROM functions include `labpc_ao_write()`, `labpc_ao_insn_write()`, `labpc_serial_out()`, `labpc_serial_in()`, `labpc_eeprom_read()`, `labpc_eeprom_write()`, `write_caldac()`, `labpc_calib_insn_write()`, and `labpc_eeprom_insn_write()`.

## Control Flow
`labpc_common_attach()` allocates `labpc_private`, selects byte-access callbacks from `dev->mmio` versus `dev->iobase`, clears command registers, optionally requests the IRQ, allocates two 8254 counter blocks, and creates five subdevices: AI, AO or unused, 8255 DIO, calibration or unused, and EEPROM or unused. Lab-PC-1200 boards get calibration and EEPROM subdevices; AO-capable boards initialize outputs to midscale.

Instruction AI reads cancel any command, program channel/gain/reference, configure command registers, clear FIFO, trigger conversions one at a time, poll data availability, and read FIFO words. Command execution first validates trigger combinations and timing, classifies scan mode, chooses transfer type based on DMA availability, wake flags, board FIFO support, and count size, programs channel/gain/range/reference, interval counter, 8254 pacers, FIFO, optional DMA, interrupt enables, external trigger/pacing bits, and finally starts software or hardware trigger under spinlock.

Interrupt handling reads status registers, rejects unrelated IRQs, handles overrun/overflow errors, drains data through ISA DMA or FIFO, clears timer interrupts, detects external stop, sets EOA when `count` reaches zero, and dispatches Comedi events.

## State And Persistence
`labpc_private` command-register shadows preserve bitfields across AI/AO/DIO/calibration operations. `count` tracks remaining samples for count-limited commands and can exceed 32 bits. `current_transfer` records whether interrupts should drain FIFO or ISA DMA. `stat1`/`stat2` cache latest status reads. Calibration and EEPROM subdevices use Comedi readback arrays; EEPROM readback is populated at attach.

## Dependencies And Integration Points
The file depends on Comedi core, 8255, 8254, Linux IRQ/delay/io helpers, `ni_labpc_regs.h`, `ni_labpc.h`, and optional ISA DMA wrappers. It exports `labpc_common_attach()` and `labpc_common_detach()` for bus-specific modules.

## Risks
Command validation and hardware programming are tightly coupled to scan direction rules; Lab-PC+ cannot scan up, while Lab-PC-1200 can. External start and external stop cannot be used together. FIFO drain has a hard timeout to avoid infinite loops. EEPROM writes are restricted to addresses 16-127, but writes still affect persistent board memory. `labpc_common_detach()` only frees `devpriv->counter`; the pacer is stored in `dev->pacer` and relies on generic cleanup. IRQ detection logic combines `stat2` even for non-1200 boards after initializing it to zero; status handling must remain careful.

## Test Signals
Tests should cover I/O versus MMIO callback selection, command-trigger validation matrix, timing rounding for convert/scan timer combinations, scan-mode chanlist validation, transfer-mode selection for DMA/FIFO/CMDF flags, FIFO drain count decrement and timeout, external stop drain path, overrun/overflow event generation, AO range bit updates and readback, calibration DAC serial writes, EEPROM readback population and user-area write restriction, attach subdevice layout for Lab-PC+ versus 1200 variants, and IRQ/no-IRQ command availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_cs.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_cs.c

## Purpose
`ni_labpc_cs.c` is the PCMCIA front end for the NI DAQCard-1200, a Lab-PC-family board. It sets up PCMCIA resources and delegates device behavior to `labpc_common_attach()`.

## Important APIs, Types, And Functions
`labpc_cs_boards[]` defines the DAQCard-1200 board info: 10 us AI speed, AO present, Lab-PC-1200 register set. `labpc_cs_auto_attach()` assigns the board pointer, enables PCMCIA I/O and IRQ resources, records the I/O base, validates IRQ presence, and calls common attach with `IRQF_SHARED`. `labpc_cs_detach()` calls common detach and disables PCMCIA. `driver_labpc_cs`, `labpc_cs_attach()`, `labpc_cs_ids[]`, and `labpc_cs_driver` register the Comedi/PCMCIA integration.

## Control Flow
PCMCIA ID `0x010b/0x0103` triggers auto config. The driver requests automatic I/O assignment plus enabled pulse IRQ. Once resources are active, it calls common attach exactly like an I/O-port Lab-PC-1200 board. All AI/AO/DIO/calibration/EEPROM behavior is then provided by `ni_labpc_common.c`.

## State And Persistence
No unique private state is allocated here. The board pointer is a static DAQCard-1200 descriptor. Runtime state is `labpc_private` from common attach and PCMCIA resource state from Comedi PCMCIA helpers.

## Dependencies And Integration Points
The file depends on Comedi PCMCIA helpers and `ni_labpc.h`. It integrates with common Lab-PC code and the Linux PCMCIA ID/probe/remove model.

## Risks
The device requires an IRQ; `labpc_cs_auto_attach()` fails with `-EINVAL` if PCMCIA enable does not provide one. The comments document DAQCard-1200-specific chanlist quirks that are enforced in common scan validation through board flags. Resource flags include pulse IRQ behavior, so changing PCMCIA config flags can break interrupt delivery.

## Test Signals
Tests should confirm PCMCIA ID matching, config flags before enable, I/O base assignment, no-IRQ failure, shared IRQ handoff to common attach, common attach failure propagation, detach ordering, and DAQCard-1200 board flags reflected in common subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.c

## Purpose
`ni_labpc_isadma.c` provides optional ISA DMA support for Lab-PC ISA boards. It is split from the common driver so non-ISA bus front ends can share common logic without always depending on ISA DMA.

## Important APIs, Types, And Functions
The module exports `labpc_setup_dma()`, `labpc_drain_dma()`, `labpc_handle_dma_status()`, `labpc_init_dma_chan()`, and `labpc_free_dma_chan()`. `labpc_suggest_transfer_size()` computes a DMA buffer size targeting at most one third of a second per transfer and respecting sample size and descriptor max size. `handle_isa_dma()` drains current DMA data, reprograms the descriptor when more data is expected, and clears the board DMA terminal-count interrupt.

## Control Flow
The ISA front end calls `labpc_init_dma_chan()` after common attach if an IRQ exists. Only DMA channels 1 and 3 are accepted; a single read buffer of `0xff00` bytes is allocated. During command setup, common code calls `labpc_setup_dma()` when it selects `isa_dma_transfer`. That computes descriptor size, clamps to remaining count for count-limited commands, programs the ISA DMA controller, and sets `CMD3_DMAEN | CMD3_DMATCINTEN` in the common command-register shadow. On interrupts, common code calls `labpc_handle_dma_status()`; if terminal count or external stop status is present, `handle_isa_dma()` drains and optionally reprograms DMA.

`labpc_drain_dma()` disables host DMA to get residue, computes received samples, updates `devpriv->count`, adjusts next descriptor size, and writes samples from the DMA buffer to the Comedi async buffer.

## State And Persistence
The persistent DMA pointer lives in `devpriv->dma`. The active descriptor's `size`, `maxsize`, `virt_addr`, and channel are maintained by Comedi ISA DMA helpers. `devpriv->count` and `devpriv->cmd3` are shared with common command/interrupt code.

## Dependencies And Integration Points
The file depends on `comedi_isadma`, `ni_labpc.h`, `ni_labpc_regs.h`, and `ni_labpc_isadma.h`. It exports GPL symbols consumed by `ni_labpc_common.c` and `ni_labpc.c` when `CONFIG_COMEDI_NI_LABPC_ISADMA` is enabled.

## Risks
DMA sizing uses integer frequency calculations and can overflow/underestimate for unusual trigger values if command validation changes. Residue handling is critical for external stop triggers. Only channels 1 and 3 are valid; invalid channels silently leave DMA unavailable. Shared mutation of `cmd3` means common code must write the command register after DMA setup.

## Test Signals
Tests should cover valid/invalid DMA channel allocation, descriptor size for timer and non-timer commands, count-limited clamping, sample-size alignment, residue-to-sample conversion, count decrement and leftover calculation, reprogramming when leftover remains, terminal-count status detection for Lab-PC+ and Lab-PC-1200, interrupt clear write, and free path with null DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.h

## Purpose
`ni_labpc_isadma.h` is the conditional interface for optional Lab-PC ISA DMA support. It lets common and ISA front-end code call DMA hooks regardless of whether `CONFIG_COMEDI_NI_LABPC_ISADMA` is enabled.

## Important APIs, Types, And Functions
When the Kconfig option is enabled, the header declares `labpc_init_dma_chan()`, `labpc_free_dma_chan()`, `labpc_setup_dma()`, `labpc_drain_dma()`, and `labpc_handle_dma_status()`. When disabled, it defines static inline no-op versions of the same functions.

## Control Flow
Callers do not branch on Kconfig. `ni_labpc.c` can always call init/free, and `ni_labpc_common.c` can always call setup/drain/status helpers. In disabled builds, no state is allocated and DMA paths are effectively unavailable because `devpriv->dma` remains null.

## State And Persistence
The header itself has no state. Its no-op stubs preserve build compatibility while leaving all runtime DMA state absent.

## Dependencies And Integration Points
The header is included by `ni_labpc.c`, `ni_labpc_common.c`, and `ni_labpc_isadma.c`. It depends on forward-visible Comedi device/subdevice declarations from including source files.

## Risks
The no-op fallback can make user-provided DMA configuration appear accepted while no DMA is actually used. Common code's transfer selection checks `devpriv->dma`, so this should degrade to FIFO transfers, but tests should ensure no call assumes DMA side effects after a no-op setup. Signature drift between declarations and implementations would break one Kconfig variant.

## Test Signals
Test enabled and disabled Kconfig builds, no-op behavior with DMA options, common transfer selection when `devpriv->dma == NULL`, symbol export availability when enabled, and header include order in all Lab-PC compilation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_pci.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_pci.c

## Purpose
`ni_labpc_pci.c` is the PCI front end for the NI PCI-1200 Lab-PC-family board. It performs PCI resource setup and delegates the device implementation to `labpc_common_attach()`.

## Important APIs, Types, And Functions
`labpc_pci_boards[]` defines the single PCI-1200 board descriptor. `labpc_pci_mite_init()` temporarily maps BAR0 to configure the MITE I/O device window base-size register to point at BAR1. `labpc_pci_auto_attach()` validates the context, enables PCI, initializes MITE, maps BAR1 into `dev->mmio`, and calls common attach with the PCI IRQ and `IRQF_SHARED`. `labpc_pci_detach()` calls common detach and Comedi PCI detach. PCI registration uses `labpc_pci_table`, `labpc_pci_probe()`, and `module_comedi_pci_driver()`.

## Control Flow
PCI ID `PCI_VENDOR_ID_NI, 0x161` maps to the PCI-1200 board. Probe invokes Comedi PCI auto config with that board index. Auto attach sets board metadata, enables the device, sets the MITE data window, maps register MMIO BAR1, and lets common attach select MMIO byte accessors, allocate counters/subdevices, and request the shared IRQ.

## State And Persistence
The PCI front end owns no unique private state. Persistent runtime state is common `labpc_private`, Comedi PCI resource state, and BAR1 MMIO mapping. The MITE BAR0 mapping is temporary and released immediately after window setup.

## Dependencies And Integration Points
The file depends on Comedi PCI helpers, Linux interrupt definitions, MMIO mapping, and `ni_labpc.h`. It integrates with common Lab-PC code by setting `dev->mmio`, which causes `labpc_common_attach()` to use `readb`/`writeb` and MMIO 8254/8255 helpers.

## Risks
MITE setup is a minimal local copy rather than full MITE infrastructure. If BAR1 physical addressing or window setup changes, common MMIO register access fails. The IRQ is passed unconditionally from PCI; common attach may proceed without command support if IRQ request fails. Driver name is `labpc_pci`, while board name is `ni_pci-1200`, which matters for user-visible configuration.

## Test Signals
Tests should cover PCI ID matching, context validation, PCI enable failure, MITE BAR0 map failure, BAR1 map failure, MITE window write value, common attach using MMIO accessors, shared IRQ path, detach ordering, and board flags matching Lab-PC-1200 common behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_regs.h

## Purpose
`ni_labpc_regs.h` defines the Lab-PC register map and bit masks used by the common and ISA-DMA Lab-PC code. It centralizes 8-bit register offsets for status, command, FIFO, timer, DIO, calibration, EEPROM, and interval counter access.

## Important APIs, Types, And Functions
The header contains no functions. It defines status bits such as `STAT1_DAVAIL`, `STAT1_OVERRUN`, `STAT1_OVERFLOW`, `STAT1_GATA0`, `STAT2_OUTA1`, and `STAT2_FIFONHF`; command bit constructors and masks such as `CMD1_MA()`, `CMD1_GAIN()`, `CMD1_SCANEN`, `CMD2_SWTRIG`, `CMD2_HWTRIG`, `CMD3_DMAEN`, `CMD3_FIFOINTEN`, `CMD6_ADCUNI`, `CMD6_SCANUP`, and `CMD5_EEPROMCS`; and register offsets for ADC FIFO, DAC byte registers, 8255 DIO base, 8254 counters, caldac/EEPROM serial control, and interval counter programming.

## Control Flow
The macros are consumed by `ni_labpc_common.c` to build command-register shadows, program AI/AO/calibration/EEPROM paths, drain FIFOs, and decode interrupt status. `ni_labpc_isadma.c` uses terminal-count status and clear-register macros to integrate DMA completion with common interrupt handling.

## State And Persistence
The header defines symbolic access to hardware state but stores none. Its bit definitions directly shape the persistent command-register shadows in `struct labpc_private`.

## Dependencies And Integration Points
It depends only on `BIT()` being visible through included Linux headers in the consuming C files. It is included by common and ISA-DMA Lab-PC code and should remain bus-neutral because both I/O-port and MMIO front ends use the same offsets.

## Risks
Register aliases share offsets with read/write-specific meanings, such as `STAT1_REG`/`CMD1_REG` and `ADC_FIFO_REG`/`DMATC_CLEAR_REG`; using the wrong direction can corrupt hardware state. Comments mark `CMD4_REG` as "Command 3 reg", which appears to be a comment typo and should not drive code changes. Any offset or bit change affects all Lab-PC bus variants.

## Test Signals
Test signals are mostly compile/static and hardware-simulation checks: status bits decoded in interrupt paths, command shadows using the intended masks, DAC byte offsets for both channels, FIFO clear/read alias behavior, DMA terminal-count clear offset, Lab-PC-1200-only command 5/6 use, and no accidental dependency on bus type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_regs.h -->
