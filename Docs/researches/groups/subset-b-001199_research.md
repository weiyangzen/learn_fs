# Research: subset-b-001199

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_common.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_common.c

## Purpose
`ni_mio_common.c` is the shared implementation for National Instruments DAQ-STC based MIO Comedi drivers. It is intentionally included by bus-specific drivers, notably `ni_pcimio.c` with `PCIDMA` enabled and `ni_mio_cs.c` without PCI DMA support. It translates Comedi analog input, analog output, digital I/O, counter/timer, calibration, EEPROM, serial, PFI, RTSI, and global routing operations into NI E-Series, M-Series, 611x, 6143, 67xx, and related register programming.

## Important APIs, Types, And Functions
The file depends on `struct ni_board_struct` and `struct ni_private` from `ni_stc.h`. Board metadata controls channel counts, maxdata, FIFO depths, gain lookup tables, AO ranges, register family flags, calibration DACs, DIO capabilities, timing limits, and alternate route names. Private state stores shadow register copies, MITE rings/channels, AI offsets, calibration state, EEPROM buffers, PFI/RTSI routing caches, PLL clock state, and locks.

The low-level register layer consists of `ni_write{b,w,l}()` and `ni_read{b,w,l}()`, which compile to MMIO access for PCI builds and port I/O for non-PCI builds. `m_series_stc_write()`, `m_series_stc_read()`, `ni_stc_writew()`, `ni_stc_writel()`, `ni_stc_readw()`, and `ni_stc_readl()` abstract DAQ-STC windowed registers and M-Series direct register mappings. `ni_set_bitfield()` and `ni_set_bits()` update shadowed registers under `soft_reg_copy_lock`.

The analog input path is centered on `ni_ai_cmdtest()`, `ni_ai_cmd()`, `ni_ai_reset()`, `ni_ai_poll()`, `ni_ai_insn_read()`, `ni_ai_munge()`, `ni_load_channelgain_list()`, `ni_m_series_load_channelgain_list()`, `ni_clear_ai_fifo()`, FIFO drain/read helpers, and interrupt helpers `handle_a_interrupt()`/`ack_a_interrupt()`. DMA-enabled builds use `ni_request_ai_mite_channel()`, `ni_ai_setup_MITE_dma()`, `ni_sync_ai_dma()`, and `ni_ai_drain_dma()`.

The analog output path uses `ni_ao_cmdtest()`, `ni_ao_cmd()`, `ni_ao_arm()`, `ni_ao_reset()`, `ni_ao_insn_write()`, `ni_ao_insn_config()`, and smaller command-building helpers for personalization, trigger, counters, update clock, channels, stop conditions, FIFO mode, and interrupts. AO DMA uses `ni_request_ao_mite_channel()`, `ni_ao_setup_MITE_dma()`, and `ni_ao_wait_for_dma_load()`. Non-DMA builds use FIFO load helpers.

Digital and correlated digital I/O are implemented by `ni_dio_insn_config()`, `ni_dio_insn_bits()`, `ni_m_series_dio_insn_config()`, `ni_m_series_dio_insn_bits()`, `ni_cdio_cmdtest()`, `ni_cdio_cmd()`, `ni_cdo_inttrig()`, `ni_cdio_cancel()`, and `handle_cdio_interrupt()`. Counter integration maps NI-TIO counter register operations through `ni_gpct_write_register()` and `ni_gpct_read_register()` and provides optional MITE-backed counter commands with `ni_gpct_cmd()` and `ni_gpct_cancel()`.

Calibration and utility surfaces include CALDAC pack/write functions, `caldac_setup()`, EEPROM reads, M-Series EEPROM buffering consumers, PWM calibration configuration, CS5529 calibration ADC support for 67xx boards, frequency-output instructions, and serial bit-bang/hardware serial instructions. Routing surfaces include PFI helpers, RTSI helpers, PLL/master-clock selection, RGOUT0 and RTSI_BRD shared-mux reference tracking, `connect_route()`, `disconnect_route()`, `test_route()`, and `ni_global_insn_config()`.

## Control Flow
Bus wrappers allocate `struct ni_private` with `ni_alloc_private()`, set board flags and bus resources, request an IRQ, and call `ni_E_init()`. `ni_E_init()` validates the build/resource mode, assigns global signal routing tables, initializes clock output defaults, allocates `NI_NUM_SUBDEVICES`, and configures each Comedi subdevice according to the board table and private flags. It resets AI/AO hardware, creates DIO/PFI/RTSI/calibration/EEPROM/serial/frequency-output subdevices, constructs NI-TIO counters, initializes default counter outputs, programs interrupt routing, and writes initial DMA selector registers.

AI command execution follows the Comedi pattern: `ni_ai_cmdtest()` validates trigger source combinations, timing minimums, route arguments, stop counts, and rounded timer values. `ni_ai_cmd()` clears FIFO, loads channel/gain memory, disables analog triggering, programs start/stop/scan/convert counters and external route values, enables interrupts, arms STC counters, optionally prepares MITE DMA, and starts immediately, waits for an internal trigger, or waits for an external trigger. Interrupts call `ni_E_interrupt()`, which reads/acks A and B status, syncs MITE descriptors, dispatches AI/AO handlers, handles counter/CDIO events, and calls `comedi_handle_events()`.

AO command execution is deliberately split: `ni_ao_cmd()` configures the STC but leaves `ao_needs_arming` set. `ni_ao_arm()` later clears/preloads FIFO or DMA after userspace has provided output data, waits for DAC preload completion, enables interrupts, and arms UI/UC/BC counters. `ni_ao_inttrig()` can arm on demand for compatibility, then pulses AO START1. Single-sample writes bypass the command path and directly program the DAC data register after range-specific munging.

Global route control enters through `ni_global_insn_config()`. It validates a source/destination pair through `ni_route_to_register()`, checks whether the destination is already driven, and then configures PFI, RTSI, GPFO/CtrOut, or NI-TIO counter routing. RTSI routes may allocate shared intermediate muxes through RGOUT0 or NI_RTSI_BRD lines and keep usage counts so multiple outputs can share a route without premature teardown.

## State And Persistence Behavior
Runtime state is held in `dev->private` and subdevice fields only. There is no filesystem persistence. Register shadow copies are important because several STC and DMA-selection registers are shared by independent paths and must be updated atomically under locks. MITE channel pointers and rings represent transient DMA ownership and are acquired per active command, then released on reset/cancel/detach. AI offset arrays and AO configuration arrays track per-channel data format/range state for buffer munging and direct output writes.

Calibration state includes cached CALDAC values, PWM up/down counts, AI calibration source selection, and M-Series EEPROM data copied at attach time by the PCI wrapper. EEPROM subdevices expose persistent board EEPROM contents to userspace, but this file only reads them. The clock state (`clock_source`, `clock_ns`, `clock_and_fout`, `clock_and_fout2`) persists for the life of the attached device and is changed by RTSI clock configuration instructions.

## Dependencies And Integration Points
This file integrates tightly with the Comedi core (`comedi_alloc_subdevices()`, async buffers, command validation helpers, event flags, subdevice callbacks), Linux interrupt/DMA/MMIO APIs, `mite.h` DMA helpers, NI-TIO counter support, `ni_routes.h` global route tables, and `comedi_8255` callbacks. Bus-specific wrappers provide `dev->mmio` or `dev->iobase`, IRQ registration, MITE attachment, board selection, EEPROM preloading, and detach cleanup.

## Risks
The file is hardware-specific and contains many family-specific conditionals; regressions can affect only certain boards. Comments identify several uncertain or partially tested areas, including CDIO interrupt behavior, SCXI/M-Series support, FIFO/DMA exact transfer limits without DMA, 6143 support, MITE CDIO channel selection assumptions, and AO command behavior for some M-Series DAC layouts. Interrupt handlers and poll paths share state and rely on spinlocks; mistakes can cause lost samples, FIFO over/underrun, or stale DMA completion accounting. Route disconnect has a strict source comparison and shared mux refcounting, so route identity mismatches can leave muxes allocated or reject disconnects.

## Test Signals
Useful validation includes Comedi `cmdtest` coverage for AI/AO/CDIO trigger validation, attach/probe smoke tests for representative E-Series, M-Series, 611x, 6143, 67xx, and PCMCIA devices, loopback tests for PFI/RTSI/global route connect/disconnect, DMA and non-DMA streaming tests that check EOS/EOA/overflow events, direct AI/AO instruction reads/writes, DIO direction/bit tests, counter DMA tests, EEPROM/CALDAC/PWM calibration instruction checks, and interrupt/poll race tests under high sample rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_cs.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_cs.c

## Purpose
`ni_mio_cs.c` is the PCMCIA/CardBus-facing Comedi driver for National Instruments DAQCard E-Series devices. It supplies the small bus-specific shell around `ni_mio_common.c`: board identification, I/O-window allocation, IRQ request, Comedi registration, and detach cleanup.

## Important APIs, Types, And Functions
The file defines a static `ni_boards[]` table for DAQCard AI-16XE-50, AI-16E-4, 6062E, 6024E, and 6036E. Entries provide `device_id`, analog input channel count, maxdata, FIFO depth, gain lookup table, AI speed, AO capabilities where present, AO ranges, AO speed, dithering flags, and calibration DAC layout.

`ni_getboardtype()` matches the PCMCIA card id to a board entry. `mio_pcmcia_config_loop()` tries 16-bit I/O windows from `0x000` through `0x3e0` in `0x20` increments using `pcmcia_request_io()`. `mio_cs_auto_attach()` selects the board, enables the PCMCIA function, records `dev->iobase`, requests the IRQ with the shared common `ni_E_interrupt()` handler, allocates common private state, and calls `ni_E_init(dev, 0, 1)`. `mio_cs_detach()` calls `mio_common_detach()` and disables the PCMCIA device.

## Control Flow
The module registers a `pcmcia_driver` and a `comedi_driver` through `module_comedi_pcmcia_driver()`. PCMCIA probe calls `cs_attach()`, which invokes `comedi_pcmcia_auto_config()`. Comedi then calls `mio_cs_auto_attach()`: match `link->card_id`, enable the socket and I/O resource, request the card IRQ, allocate private state, and delegate full subdevice setup to `ni_E_init()`. Removal goes through `comedi_pcmcia_auto_unconfig()` and `mio_cs_detach()`.

## State And Persistence Behavior
Persistent hardware identity is represented only by the static board table and PCMCIA ids. Runtime state lives in the Comedi device, PCMCIA `link->priv`, the assigned I/O base, IRQ number, and `struct ni_private` allocated by the common implementation. No data is written to disk. PCMCIA enable/disable and IRQ ownership are balanced across attach/detach.

## Dependencies And Integration Points
The file depends on Linux module and PCMCIA support, `linux/comedi/comedi_pcmcia.h`, `comedi_8255`, `ni_stc.h`, and the included `ni_mio_common.c`. Because `PCIDMA` is not defined, the common code uses port I/O and non-MITE FIFO paths. The common code still supplies all Comedi subdevices, interrupt handling, AI/AO/DIO/calibration/routing behavior.

## Risks
The I/O-window scan is fixed and could fail on unusual resource layouts. The board match uses `card_id`, so unsupported or misreported card ids attach as `-ENODEV`. Since this build has no MITE DMA, high-rate AI/AO behavior relies on FIFO interrupts and may be more sensitive to interrupt latency. All deep device behavior comes from `ni_mio_common.c`, so board-table accuracy is critical for ranges, timing, FIFO depth, and calibration.

## Test Signals
Attach tests should verify each PCMCIA id maps to the expected board name and capabilities. Resource tests should cover successful and failed I/O allocation, IRQ request failure, detach after partial attach, and card removal while commands are active. Functional tests should cover AI direct reads, interrupt-driven AI commands, AO writes on boards with AO, DIO instructions, calibration subdevice exposure, and clean PCMCIA disable on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_mio_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcidio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcidio.c

## Purpose
`ni_pcidio.c` is the Comedi PCI driver for National Instruments PCI-DIO-32HS, PXI/PCI-6533, and PCI-6534 high-speed 32-bit digital I/O boards. It supports simple per-line DIO and timed input streaming, primarily through MITE DMA. PCI-6534 additionally requires firmware upload to its FPGAs before normal operation.

## Important APIs, Types, And Functions
The file defines register offsets and bit masks for the DIO protocol engine, FIFO, interrupt flags, port direction/data registers, DMA line control, timing registers, and PCI-6534 firmware/FPGA registers. `struct nidio_board` identifies supported board names, firmware requirements, and DIO speed. `struct nidio96_private` stores MITE attachment, board type, DIO state, cached OP mode bits, a DI MITE channel/ring, and a lock.

DMA helpers are `ni_pcidio_request_di_mite_channel()`, `ni_pcidio_release_di_mite_channel()`, `setup_mite_dma()`, and `ni_pcidio_poll()`. Interrupt handling is in `nidio_interrupt()`, which syncs/acks MITE, drains PIO FIFO data when needed, translates group flags into Comedi events, and calls `comedi_handle_events()`.

Instruction handlers are `ni_pcidio_insn_config()` for DIO direction and timing constraints, `ni_pcidio_insn_bits()` for packed 32-bit port read/write, `ni_pcidio_cmdtest()` for validating streaming commands, `ni_pcidio_cmd()` for programming timed or external-request input acquisition, `ni_pcidio_inttrig()` for internal command start, `ni_pcidio_cancel()` for stopping DMA/interrupts, and `ni_pcidio_change()` for MITE buffer updates.

PCI-6534 firmware support is implemented by `pci_6534_load_fpga()`, `pci_6534_reset_fpga()`, `pci_6534_reset_fpgas()`, `pci_6534_init_main_fpga()`, and `pci_6534_upload_firmware()`, using `comedi_load_firmware()` and the declared firmware filenames.

## Control Flow
PCI probe calls `ni_pcidio_pci_probe()`, which delegates to Comedi PCI auto-config. `nidio_auto_attach()` selects the board by driver data, enables PCI resources, allocates private state, attaches MITE, allocates a DI ring, optionally uploads PCI-6534 firmware, resets board DIO/interrupt state, allocates one DIO subdevice, assigns instruction/command/poll callbacks, and requests the shared IRQ.

For simple DIO, Comedi instruction calls update `s->io_bits` and `s->state`, then write `PORT_PIN_DIRECTIONS(0)` or `PORT_IO(0)` and read back `PORT_IO(0)`. For streaming input, `ni_pcidio_cmdtest()` accepts `TRIG_NOW`/`TRIG_INT` starts, `TRIG_TIMER`/`TRIG_EXT` scan begins, `TRIG_NOW` conversion, counted scan ends, and counted or continuous stop. `ni_pcidio_cmd()` forces ports to input, configures all four FIFOs as a 32-bit data path, programs internal or external REQ protocol registers, sets transfer count for counted acquisitions, sets up MITE DMA, clears/enables interrupts, and either starts immediately or installs `ni_pcidio_inttrig()`.

The interrupt handler loops while status reports data left, but caps work to avoid interrupt livelock. It handles transfer-ready PIO fallback, count-expired EOA, waited errors, primary/secondary terminal count EOA, and then reports events to Comedi.

## State And Persistence Behavior
Runtime state is transient and device-local: MITE ring/channel ownership, cached `OP_MODEBits`, subdevice direction/state, and IRQ registration. Firmware blobs are loaded into PCI-6534 FPGA hardware on attach but are not persisted by the driver. The driver declares firmware requirements with `MODULE_FIRMWARE`, so availability is an external deployment concern.

## Dependencies And Integration Points
The driver uses Comedi PCI helpers, Comedi async buffers/events, Linux IRQ/MMIO APIs, MITE DMA helpers, and kernel firmware loading through `comedi_load_firmware()`. The PCI id table maps NI vendor/device ids to board entries, and `module_comedi_pci_driver()` wires the Comedi and PCI driver lifecycles together.

## Risks
The file comments state handshaking is not supported and DMA mostly works only for timed input. DMA channel selection is constrained to channels 1-2. The interrupt handler includes work caps, indicating risk of excessive interrupt processing. PCI-6534 attach can fail if firmware files are missing or FPGA status polling times out. The code contains old comments and some broad assumptions around transfer widths, external trigger semantics, and continuous stop behavior.

## Test Signals
Tests should cover PCI id binding, attach/detach with and without firmware, firmware failure paths, DIO direction and packed bit operations, command validation for timer and external REQ modes, DMA setup/cancel/reuse, interrupt-driven EOA and error events, polling synchronization, and partial attach cleanup after MITE or IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcidio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcimio.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcimio.c

## Purpose
`ni_pcimio.c` is the PCI/PXI/PCIe Comedi wrapper for NI PCI-MIO E-Series, M-Series, S-Series 6143, 611x, 67xx, and many related multifunction DAQ boards. It provides the large PCI board capability table, MITE setup, board-family flag derivation, M-Series EEPROM preload, 6143 initialization, IRQ setup, PCI id binding, and detach cleanup. Core subdevice behavior is provided by the included `ni_mio_common.c` with `PCIDMA` enabled.

## Important APIs, Types, And Functions
The file defines AO range tables for E-Series external reference and M-Series 625x/628x variants, an `enum ni_pcimio_boardid`, and a large `ni_boards[]` table. Each board entry records the Comedi-visible name, optional alternate routing name, AI/AO channel counts and maxdata, FIFO depths, gain table, speed limits, register family, 8255/32-DIO flags, calibration DACs, and DIO timing.

`pcimio_ai_change()`, `pcimio_ao_change()`, `pcimio_gpct0_change()`, `pcimio_gpct1_change()`, and `pcimio_dio_change()` adapt Comedi buffer changes to the corresponding MITE rings. `m_series_init_eeprom_buffer()` temporarily maps a MITE I/O window and copies M-Series calibration EEPROM bytes into `devpriv->eeprom_buffer`. `init_6143()` programs board-specific registers for the simultaneous-sampling 6143 path. `pcimio_auto_attach()` performs PCI attach and delegates common subdevice construction to `ni_E_init()`. `pcimio_detach()` frees IRQs, MITE rings, MITE attachment, MMIO mapping, and PCI resources.

## Control Flow
The PCI table maps NI device ids to board ids. Probe calls `comedi_pci_auto_config()`, which invokes `pcimio_auto_attach()` with the board id. Attach enables PCI resources, allocates common private state, attaches MITE using window 0, derives private family flags from `board->reg_type`, allocates five MITE rings, preloads M-Series EEPROM or initializes 6143 hardware when applicable, requests the IRQ, and calls `ni_E_init(dev, 0, 1)`. After common initialization, attach installs per-subdevice buffer-change callbacks so Comedi async buffer changes update the proper MITE descriptors.

Detach first calls `mio_common_detach()` to destroy NI-TIO counter state, then releases the IRQ, frees all rings, detaches MITE, unmaps MMIO if present, and disables PCI resources. Driver registration is handled by `module_comedi_pci_driver()`.

## State And Persistence Behavior
The board table is static metadata. Runtime state lives in `struct ni_private`, MITE rings/channels, the copied M-Series EEPROM buffer, Comedi subdevices, IRQ state, and MMIO mapping. The EEPROM preload reads persistent hardware calibration data but stores only a volatile copy. The wrapper itself does not write persistent hardware configuration or filesystem state.

## Dependencies And Integration Points
This file depends on Linux PCI/module support, `linux/comedi/comedi_pci.h`, `mite.h`, `ni_stc.h`, and the included common implementation. With `PCIDMA` defined, `ni_mio_common.c` compiles PCI DMA paths, MMIO register accessors, CDIO DMA, GPCT DMA, and MITE-backed AI/AO streaming.

## Risks
The board table is broad and a wrong field can misconfigure channels, timing, FIFO depth, ranges, calibration, register family behavior, or route lookup. Attach has many allocation steps; cleanup relies on detach after partial failures. `m_series_init_eeprom_buffer()` temporarily reprograms MITE window registers and must restore them correctly. Some boards use alternate route names, guessed FIFO depths, or comments noting unsupported/broken features such as SCXI on M-Series and DIO on 673x.

## Test Signals
Validation should include PCI id table coverage, representative attach/detach for each register family, MITE ring allocation failure paths, M-Series EEPROM readback, 6143 initialization, buffer-change callbacks, IRQ request failure behavior, and end-to-end AI/AO/DIO/counter command tests through the common code. Board metadata can be checked by comparing expected Comedi subdevice counts, ranges, maxdata, and timing constraints per board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcimio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.c

## Purpose
`ni_routes.c` is a helper module for National Instruments Comedi signal routing. It assigns per-device route tables, sorts route metadata for efficient search, validates source-to-destination pairs, converts valid routes to hardware register values, enumerates valid routes for userspace, and reverse-maps register values back to NI global signal names.

## Important APIs, Types, And Functions
The module operates on `struct ni_route_tables`, `struct ni_device_routes`, and `struct ni_route_set` from `ni_routes.h`. Route values come from generated/static routing headers `ni_routing/ni_route_values.h` and `ni_routing/ni_device_routes.h`. `RVi()` indexes the flattened destination-by-source register-value matrix; `B()` converts NI global names to table indexes, and `V()`/`UNMARK()` mark/unmark valid register values.

Exported APIs include `ni_assign_device_routes()`, `ni_count_valid_routes()`, `ni_get_valid_routes()`, `ni_is_cmd_dest()`, `ni_sort_device_routes()`, `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_lookup_route_register()`, `ni_route_to_register()`, and `ni_find_route_source()`. Internal helpers locate route-value tables by device family and valid-route tables by board name or alternate board name, sort destination/source arrays, and implement bsearch comparators.

## Control Flow
At module init, `ni_sort_all_device_routes()` walks every entry in `ni_device_routes_list` and calls `ni_sort_device_routes()`. Sorting counts route sets until a zero destination sentinel, sorts route sets by destination, counts each source list until a zero sentinel, and sorts sources. Runtime users call `ni_assign_device_routes()` during device attach to bind a board to its family register-value table and valid-route set. Query paths then use binary search for destination route sets and sources.

`ni_route_to_register()` first verifies that a destination exists for the device and that the requested source is listed as valid. It then looks up the direct register value. If the destination is an RTSI channel and no direct route exists, it tries indirect routing through `NI_RGOUT0` or `NI_RTSI_BRD(0..3)` and returns special register encodings when a shared mux is needed. `ni_get_valid_routes()` enumerates all direct and valid indirect RTSI routes into source/destination pairs for Comedi `INSN_DEVICE_CONFIG_GET_ROUTES`.

## State And Persistence Behavior
The module mutates route metadata in memory by sorting `ni_device_routes_list` at module init and setting `n_route_sets`/`n_src` counts. It does not allocate persistent storage, write files, or persist user choices. Assigned route tables are stored by caller-owned `struct ni_route_tables`.

## Dependencies And Integration Points
The code depends on kernel `sort()`, `bsearch()`, `slab`, Comedi global route names/macros, and the generated NI routing headers. It exports symbols used by NI MIO and NI-TIO integration code to validate Comedi trigger arguments, global route connect/disconnect operations, and route enumeration.

## Risks
The route arrays rely on sentinel values and module-init sorting. If a caller used route tables before module init sorting, binary searches would be invalid; normal module initialization avoids that. Invalid or incomplete generated route data can make valid hardware routes unavailable or expose wrong register values. The indirect RTSI encoding is compact and caller-sensitive: consumers must understand `BIT(6)` as a shared mux requirement and not a direct register value.

## Test Signals
Tests should cover table assignment by family/board/alternate board name, route count/enumeration consistency, direct and indirect RTSI route conversion, invalid source/destination bounds, reverse lookup by register value, sorting idempotence, bsearch behavior after sorting, and integration with MIO global connect/disconnect and command-trigger validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routes.c -->
