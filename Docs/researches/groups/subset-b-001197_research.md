# subset-b-001197 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt3000.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt3000.c

### Purpose
`dt3000.c` is the Comedi PCI auto-config driver for Data Translation DT3000-family data acquisition boards. It exposes synchronous analog input, optional analog output, 8-bit digital I/O, a read-only firmware/code memory subdevice, and an interrupt-backed AI command path for boards with an IRQ.

### Important APIs, Types, And Functions
Board capabilities are described by `struct dt3k_boardtype` and `dt3k_boardtypes[]`; runtime FIFO cursors live in `struct dt3k_private`. Core helpers are `dt3k_send_cmd()`, `dt3k_readsingle()`, `dt3k_writesingle()`, `dt3k_ai_empty_fifo()`, `dt3k_ai_cmdtest()`, `dt3k_ai_cmd()`, `dt3k_ai_cancel()`, `dt3k_interrupt()`, `dt3k_ai_insn_read()`, `dt3k_ao_insn_write()`, DIO insn handlers, and `dt3000_auto_attach()`.

### Control Flow
Attach selects a board from PCI `driver_data`, enables PCI, maps BAR0 dual-ported RAM, optionally requests a shared IRQ, then creates AI, AO, DIO, and memory subdevices. Single-sample AI/AO writes command parameters into DPR mailboxes and waits for firmware completion. AI commands write a chanlist into ADC buffer RAM, program scan/convert timers, configure trigger and FIFO threshold parameters, enable ADC interrupts, then start the AI subsystem. The interrupt handler drains available samples from the board FIFO into the Comedi async buffer and flags errors/end-of-acquisition.

### State, Persistence, And Dependencies
Persistent state is mostly board metadata, mapped DPR memory, optional IRQ ownership, AO readback, DIO state/io direction, and `dt3k_private` FIFO cursors. It depends on Comedi PCI helpers, Comedi async buffers, Comedi trigger validation, Linux IRQ handling, and board DSP firmware mailbox semantics.

### Integration Points
The driver registers through `module_comedi_pci_driver()`, probes DT PCI IDs, and uses `comedi_pci_auto_config()`/`comedi_pci_auto_unconfig()`. Subdevice callbacks form the user-facing Comedi ABI. `dev->read_subdev` points async reads at the AI subdevice when an IRQ is available.

### Risks
The file comments state AI commands may not work; the interrupt handler has FIXME notes, assumes a shared interrupt belongs to the card after reading the flag, and forces EOA after ten interrupts through `debug_n_ints`. Timer conversion notes are marked as needing improvement. FIFO cursor handling and command mailbox timeout behavior are hardware-sensitive.

### Test Signals
Exercise PCI probe for every DT3000 ID, BAR0 mapping, single AI/AO reads and writes, DIO direction by nibble, memory reads, IRQ and no-IRQ attachment, AI command validation/rounding, scan timing, FIFO wraparound, error interrupt bits, cancellation, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt3000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt9812.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt9812.c

### Purpose
`dt9812.c` is the Comedi USB driver for the Data Translation DT9812 module. It supports control-pipe style digital input/output, analog input, and analog output through firmware register commands; bulk streaming endpoints are discovered but not implemented.

### Important APIs, Types, And Functions
USB command layout is defined by `struct dt9812_usb_cmd` and its flash, read, write, and RMW payloads. `struct dt9812_private` stores the mutex, command endpoint addresses/sizes, and detected personality device ID. Important paths are `dt9812_find_endpoints()`, `dt9812_reset_device()`, `dt9812_read_info()`, multi-register read/write/RMW helpers, `dt9812_analog_in()`, `dt9812_analog_out()`, DIO/AIO Comedi insn handlers, `dt9812_auto_attach()`, and `dt9812_detach()`.

### Control Flow
Probe calls Comedi USB auto-config. Attach allocates private data, records it on the USB interface, validates the five endpoint layout, reads board information from flash diagnostics memory, and selects bipolar 10 V or unipolar 2.5 V ranges based on device ID. Every I/O operation takes the private mutex, builds a 32-byte firmware command for the write pipe, uses `usb_bulk_msg()` with a one second timeout, and optionally reads the response pipe. AI configures gain, mux, and ADC start in one RMW batch, then reads status/high/low registers. AO enables the selected DAC and writes low then high bytes.

### State, Persistence, And Dependencies
Persistent driver state is endpoint metadata, the device variant, mutex serialization, DO state, and AO readback values. Hardware state persists in C8051 special function registers, DAC output registers, and GPIO ports. Dependencies include Comedi USB helpers, USB bulk messaging, endian conversion for flash fields, and Silicon Labs C8051 register definitions.

### Integration Points
The USB table matches vendor/product `0867:9812`, and `module_comedi_usb_driver()` binds the Comedi and USB drivers. The driver exposes four Comedi subdevices: DI, DO, AI, and AO.

### Risks
All command writes must be 32 bytes, and the code relies on endpoint order rather than only descriptors. `dt9812_do_insn_bits()` ignores a write error from `dt9812_digital_out()`. AI assumes USB latency is enough for conversion completion and does not return an error if ADC status is not complete after the read. USB reset-on-reload behavior is heuristic.

### Test Signals
Test both DT9812-10V and DT9812-2.5V variants, endpoint direction validation, detach during I/O, short USB responses returning `-EREMOTEIO`, flash board-info reads, DI bit packing, DO state writes, AI mux/gain selection, AO readback defaults, and unsupported device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt9812.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dyna_pci10xx.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/dyna_pci10xx.c

### Purpose
`dyna_pci10xx.c` is the Comedi PCI driver for the Dynalog India PCI-1050 DAQ card, identified using a PLX vendor/device ID. It provides synchronous analog input/output and 16-bit digital input/output.

### Important APIs, Types, And Functions
`struct dyna_pci10xx_private` stores a mutex and BAR3 I/O base. `range_pci1050_ai` and `range_codes_pci1050_ai[]` define AI range programming. Important handlers include `dyna_pci10xx_insn_read_ai()`, `dyna_pci10xx_insn_write_ao()`, `dyna_pci10xx_di_insn_bits()`, `dyna_pci10xx_do_insn_bits()`, `dyna_pci10xx_auto_attach()`, and `dyna_pci10xx_detach()`.

### Control Flow
Attach enables the PCI device, records BAR2 as `dev->iobase` for analog registers and BAR3 for digital registers, initializes the mutex, and creates AI, AO, DI, and DO subdevices. AI writes channel/range to the analog control port, waits briefly, polls bit 15 for conversion complete via `comedi_timeout()`, masks 12-bit data, and returns sample count or error. AO writes sample words to the analog base. DI/DO read or update BAR3 state under the same mutex.

### State, Persistence, And Dependencies
State is limited to the BAR addresses, mutex, DO subdevice state, and Comedi subdevice descriptors. Hardware output state persists on the card. The driver depends on port I/O, PCI resource setup, Comedi DIO helpers, and Comedi timeout polling.

### Integration Points
The driver binds to `PCI_VENDOR_ID_PLX, 0x1050`, registers through `module_comedi_pci_driver()`, and uses standard Comedi auto-config/remove helpers.

### Risks
The PCI ID is not a real Dynalog vendor ID, so PLX-ID collisions are possible. `READ_TIMEOUT` is unused; conversion timeout policy depends on Comedi defaults. Memory barriers before port I/O are conservative but not a substitute for hardware documentation. AO lacks readback allocation and does not mirror output state.

### Test Signals
Validate BAR selection, AI range code programming, EOC timeout paths, all 16 AI channels, AO writes, DI/DO bit masks, mutex serialization under concurrent subdevice use, detach mutex destruction, and probe rejection on missing resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dyna_pci10xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/fl512.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/fl512.c

### Purpose
`fl512.c` is a legacy Comedi driver for an FL512 I/O-port board with 16 analog input channels and two analog output channels. Digital I/O is explicitly not supported.

### Important APIs, Types, And Functions
The file defines a small I/O map, `range_fl512`, and three driver callbacks: `fl512_ai_insn_read()`, `fl512_ao_insn_write()`, and `fl512_attach()`.

### Control Flow
Legacy attach validates and reserves a 16-byte I/O region supplied by user configuration, then creates AI and AO subdevices. AI selects the mux channel, starts each conversion, waits a fixed `usleep_range(30, 100)` instead of polling a done flag, reads LSB then MSB from overlapping registers, masks to 12 bits, and returns samples. AO writes LSB then MSB to the selected channel data register and performs an input read on the trigger register to latch conversion; final AO value is stored in Comedi readback.

### State, Persistence, And Dependencies
Persistent state is the requested I/O port reservation and AO readback buffer. Hardware analog outputs persist on the board. The driver depends on legacy Comedi attach/detach, port I/O, fixed board timing, and Comedi readback allocation.

### Integration Points
It registers with `module_comedi_driver()` and is configured manually by I/O base address. The two subdevice callbacks expose the whole hardware surface.

### Risks
There is no device ID or runtime detection. AI uses a delay instead of an end-of-conversion flag, so timing can be either too slow or too fast on real hardware. The range table declares four ranges but initializes seven entries, which is suspicious for range indexing. AO data and trigger registers intentionally overlap and rely on board-specific behavior.

### Test Signals
Test attach with valid/invalid base alignment, all AI channels, repeated AI samples at each supported range index, AO write/readback for both channels, I/O region cleanup, and timing sensitivity under CPU load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/fl512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/gsc_hpdi.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/gsc_hpdi.c

### Purpose
`gsc_hpdi.c` is the Comedi PCI driver for General Standards PCI/PMC HPDI32 high-speed parallel digital interface boards. It implements receive-mode, command-driven 32-bit digital input using PLX9080 chained DMA; transmit is documented as unsupported.

### Important APIs, Types, And Functions
`struct hpdi_private` owns PLX MMIO, DMA buffers, descriptor ring metadata, FIFO sizes, DMA descriptor index, finite sample count, and block size. Main functions are `gsc_hpdi_init_plx9080()`, `gsc_hpdi_init()`, `gsc_hpdi_setup_dma_descriptors()`, `gsc_hpdi_cmd_test()`, `gsc_hpdi_cmd()`, `gsc_hpdi_interrupt()`, `gsc_hpdi_drain_dma()`, `gsc_hpdi_cancel()`, `gsc_hpdi_auto_attach()`, and `gsc_hpdi_detach()`.

### Control Flow
Attach enables PCI bus mastering, maps PLX BAR0 and HPDI BAR2, initializes PLX DMA mode, requests IRQ, allocates four coherent 64 KiB data buffers and 256 coherent descriptors, sets the default descriptor block size, creates one DIO command subdevice, and resets/enables board interrupts. Command setup rejects output mode, resets RX FIFO and DMA, writes the first descriptor pointer to PLX, starts DMA0, initializes finite or indefinite `dio_count`, clears RX error flags, enables RX-full interrupt, and enables RX. Interrupts verify PLX interrupt ownership, clear HPDI/PLX interrupt sources, drain all completed DMA blocks into the Comedi buffer, detect RX overrun/underrun, and signal EOA when finite count reaches zero.

### State, Persistence, And Dependencies
Persistent state includes coherent DMA buffers/descriptors, circular descriptor topology, subdevice direction bits, block size from `INSN_CONFIG_BLOCK_SIZE`, FIFO size readings, IRQ ownership, and PLX/board MMIO mappings. Dependencies include `plx9080.h`, coherent DMA APIs, Comedi async buffers, shared IRQ handling, and spinlock-protected PLX DMA control registers.

### Integration Points
The driver binds PLX9080 subsystem ID `0x2400`, uses `comedi_pci_auto_config()`, and exposes block-size configuration plus `SDF_CMD_READ` on a 32-channel DIO subdevice.

### Risks
Only RX path is implemented. Descriptor/block-size changes affect interrupt cadence and buffer accounting. The drain loop infers completed blocks from PLX current address and has only an XXX note for overrun detection. Finite counts are counted in 32-bit samples while DMA block sizing is byte-based. DMA descriptor alignment and cleanup on partial attach failure are critical.

### Test Signals
Test DMA allocation failure unwind, descriptor lengths including non-word-aligned requests, finite and continuous commands, chanlist ordering validation, RX FIFO overrun/underrun flags, shared IRQ filtering, cancellation, repeated block-size reconfiguration, and detach with active DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/gsc_hpdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/icp_multi.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/icp_multi.c

### Purpose
`icp_multi.c` drives the Inova ICP_MULTI PCI board for synchronous AI, AO, DI, and DO. Comments state interrupts, counters, and DMA are not implemented.

### Important APIs, Types, And Functions
The file defines ADC/DAC/DIO/interrupt register bits, shared analog range tables, `range_codes_analog[]`, and callbacks `icp_multi_ai_insn_read()`, `icp_multi_ao_insn_write()`, `icp_multi_di_insn_bits()`, `icp_multi_do_insn_bits()`, `icp_multi_reset()`, and `icp_multi_auto_attach()`.

### Control Flow
Attach enables PCI, maps BAR2, allocates four subdevices, resets board outputs/interrupt status, and configures AI/AO/DI/DO. AI builds an ADC CSR from channel, range, and single-ended/differential mode, starts each conversion, delays briefly, polls busy clear, and reads 12-bit data from the AI register. AO selects channel/range, waits until DAC not busy, writes the sample, starts conversion, and stores readback. DIO uses direct 16-bit/8-bit register reads and writes.

### State, Persistence, And Dependencies
State is the mapped MMIO region, AO readback, DO state, and board output state after reset. The driver depends on Comedi PCI helpers, Comedi timeout polling, port-width MMIO accessors, and range/reference encoding in Comedi chanspecs.

### Integration Points
PCI ID `PCI_VENDOR_ID_ICP, 0x8000` auto-configures this driver. Comedi users see four simple instruction-only subdevices.

### Risks
Counter and interrupt registers are reset but not exposed. AI does not validate differential channel range beyond composing the CSR. Reset forces all AO channels to 0 V in 0..5 V range, which may be observable on attach. AO readback depends on successful readback allocation only.

### Test Signals
Test PCI probe and BAR2 mapping, reset side effects, all AI ranges and references, AI timeout, AO busy timeout and readback, DI/DO widths, interrupt status clearing, and detach through `comedi_pci_detach()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/icp_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ii_pci20kc.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ii_pci20kc.c

### Purpose
`ii_pci20kc.c` is a legacy memory-mapped Comedi driver for Intelligent Instruments PCI-20001C carrier boards and up to three add-on modules. It supports carrier DIO on -2A boards, PCI-20006M AO modules, and PCI-20341M AI modules.

### Important APIs, Types, And Functions
The file defines carrier/module ID values, module register maps, `ii20k_ao_ranges`, `ii20k_ai_ranges`, and key callbacks `ii20k_init_module()`, `ii20k_ao_insn_write()`, `ii20k_ai_setup()`, `ii20k_ai_insn_read()`, `ii20k_dio_config()`, DIO insn handlers, `ii20k_attach()`, and `ii20k_detach()`.

### Control Flow
Attach validates a manually supplied memory base, reserves and maps 0x400 bytes, reads the carrier ID to determine DIO availability and module-empty bits, then allocates four subdevices: one per module slot and one carrier DIO subdevice. Module initialization switches on the module ID and configures AO, AI, or unused. AO writes offset-munged 16-bit values LSB/MSB then strobes. AI initializes the module for software conversion, programs gain-dependent settling timing and chanlist, triggers conversion through a pacer-reset read, waits for interrupt flag clear, reads LSB/MSB, and converts two's-complement to offset binary. DIO configures full 8-bit ports as input or output and writes only changed ports.

### State, Persistence, And Dependencies
Persistent state is the manually reserved memory region, MMIO mapping, subdevice module layout, per-AO readback, and DIO `io_bits`/state. It depends on fixed carrier slot offsets, Comedi legacy config, Comedi range munger helpers, and byte MMIO ordering.

### Integration Points
The driver uses `module_comedi_driver()` rather than PCI auto-detection, despite the PCI name. It integrates module identity bits into Comedi subdevice discovery.

### Risks
Manual memory-base configuration is fragile and limited to the driver's hard-coded address mask. Module probing trusts register IDs. DIO port configuration is coarse-grained by 8-bit port. In `ii20k_dio_config()`, `ctrl23` receives both `II20K_CTRL01_SET` and `II20K_CTRL23_SET`, which looks suspicious but may match hardware bit layout.

### Test Signals
Test invalid and conflicting memory bases, both carrier IDs, empty and populated slots for all supported module IDs, AO readback, AI gains/timing, DIO per-port direction changes, detach unmap/release, and unknown module IDs becoming unused subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ii_pci20kc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.c

### Purpose
`jr3_pci.c` is the Comedi PCI driver for JR3 force/torque sensor boards with one to four DSP/sensor blocks. It loads DSP firmware, initializes sensors through a timer-driven state machine, and exposes filtered force/moment/vector plus model/serial channels as analog input.

### Important APIs, Types, And Functions
Board variants are `struct jr3_pci_board`. Device and subdevice state use `struct jr3_pci_dev_private` and `struct jr3_pci_subdev_private`. Important helpers include `read_idm_word()`, `jr3_check_firmware()`, `jr3_write_firmware()`, `jr3_download_firmware()`, `jr3_pci_poll_subdevice()`, `jr3_pci_poll_dev()`, `jr3_pci_alloc_spriv()`, `jr3_pci_ai_read_chan()`, `jr3_pci_ai_insn_read()`, `jr3_pci_auto_attach()`, and `jr3_pci_detach()`.

### Control Flow
Attach selects board count from PCI ID, checks BAR0 size, maps the register window, creates one AI subdevice per sensor block, allocates per-subdevice range/maxdata lists, resets each DSP block, loads `comedi/jr3pci.idm` to all blocks, waits briefly, logs firmware copyright, then starts a timer. The timer polls each sensor: wait for valid model/serial and no watchdog errors, wait for offsets to stabilize, install an identity transform, set full scales from maximum full scales, build channel range tables, use offset 0, zero offsets, issue set-offset, and mark the sensor done. AI reads return `-EAGAIN` until done or if watchdog/sensor-change errors force reinitialization.

### State, Persistence, And Dependencies
Persistent state includes the timer, sensor MMIO pointers, per-subdevice poll state, serial/model/error caches, dynamic range tables, firmware-loaded DSP memory, and mapped BAR0. It depends on `jr3_pci.h` register layouts, firmware loader APIs, timer callbacks, spinlock protection around polling, Comedi PCI helpers, and little 16-bit values stored in 32-bit PCI words.

### Integration Points
`MODULE_FIRMWARE("comedi/jr3pci.idm")` declares the runtime firmware dependency. PCI IDs choose one to four Comedi AI subdevices. The driver’s `open` method logs per-sensor serial numbers.

### Risks
Correct operation depends on external non-free firmware and the IDM parser accepting the file. Timer polling touches MMIO under `dev->spinlock` and must be shut down synchronously on detach. Dynamic range construction happens only after sensor initialization. Sensor errors restart polling and user reads see `-EAGAIN`. `static const struct jr3_pci_board *board` in attach is unnecessarily static.

### Test Signals
Test firmware missing, malformed, and valid IDM files; one-, two-, three-, and four-sensor PCI IDs; BAR length rejection; timer shutdown on detach; sensor absent/changed/watchdog states; transition to done; channel reads for filters/model/serial; and range/maxdata list correctness after full-scale setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.h -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.h

### Purpose
`jr3_pci.h` defines the MMIO layout and helper accessors for the JR3 DSP/sensor memory consumed by `jr3_pci.c`. It models a 16-bit DSP memory space where each word is aligned on a 32-bit PCI boundary.

### Important APIs, Types, And Functions
Inline accessors `get_u16()`, `set_u16()`, `get_s16()`, and `set_s16()` wrap `readl()`/`writel()` with 16-bit casts. Key layout types are `struct raw_channel`, `struct force_array`, `struct six_axis_array`, `struct thresh_struct`, `struct le_struct`, `struct intern_transform`, `struct jr3_sensor`, and `struct jr3_block`. Enumerations describe vector bits, warning bits, `enum error_bits_t`, and transform link types.

### Control Flow
The header has no runtime control flow, but its layout drives every MMIO read/write in `jr3_pci.c`. The driver indexes `struct jr3_block` per subdevice, writes firmware into `program_lo`/`program_hi`, resets through `reset`, and reads or commands the embedded `struct jr3_sensor`.

### State, Persistence, And Dependencies
The structures represent persistent board/DSP memory: raw sensor channels, calibration and full-scale data, offsets, filtered force arrays, rate/peak data, command words, counters, warnings/errors, load envelopes, and transforms. It depends on Linux I/O accessors and exact hardware offsets documented in comments.

### Integration Points
`jr3_pci.c` includes this header to issue DSP commands, parse sensor status, expose Comedi channels, and enforce `BUILD_BUG_ON(sizeof(struct jr3_block) != 0x80000)`.

### Risks
Any field size or padding change breaks hardware ABI. Comments are extensive but no explicit compile-time assertions cover the inner `struct jr3_sensor` offsets. The accessors discard high 16 bits, matching hardware assumptions but hiding unexpected nonzero upper data. The header is not protected by an include guard.

### Test Signals
Build should verify `struct jr3_block` size. Hardware tests should confirm firmware writes land in low/high program memory, command-word completion works, filter/full-scale/error offsets match expected values, and model/serial/copyright reads are sane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ke_counter.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ke_counter.c

### Purpose
`ke_counter.c` is the Comedi PCI driver for Kolter Electronic PCI Counter cards. It exposes three 25-bit counter channels and three digital output bits.

### Important APIs, Types, And Functions
The file defines per-counter register offsets, oscillator selection bits, `ke_counter_insn_read()`, `ke_counter_insn_write()`, `ke_counter_insn_config()`, `ke_counter_do_insn_bits()`, `ke_counter_reset()`, and `ke_counter_auto_attach()`.

### Control Flow
Attach enables PCI, records BAR0 as an I/O port base, allocates counter and DO subdevices, sets the oscillator to 20 MHz, and resets all counters. Counter writes split a 32-bit value into sign/MSB/MID/LSB registers in required order. Counter reads latch by reading the latch register, then reconstruct the 32-bit value from LSB/MID/MSB/sign bytes. Config supports clock source set/get and reset. DO writes update `s->state` and output it to a single register.

### State, Persistence, And Dependencies
Persistent state is the PCI I/O base, selected oscillator source in hardware, counter values in hardware, and DO state. Dependencies include Comedi PCI auto-config, port I/O, Comedi counter config constants such as `KE_CLK_20MHZ`, and DIO state helpers.

### Integration Points
The PCI table matches `PCI_VENDOR_ID_KOLTER, 0x0014`, and the driver registers through `module_comedi_pci_driver()`. Comedi instruction config is the primary control surface for clock source and reset.

### Risks
The subdevice maxdata is `0x01ffffff`, but read/write paths move four full bytes including a sign register, so value interpretation depends on board semantics. Writes use `data[0]` for every sample instead of `data[i]`. Clock source readback rejects unknown register values.

### Test Signals
Test 20 MHz/4 MHz/external clock set and get, reset behavior, read latch ordering, writes with boundary values, DO bits, PCI BAR0 availability, and detach cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ke_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/me4000.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/me4000.c

### Purpose
`me4000.c` is the Comedi PCI driver for Meilhaus ME-4000 series boards. It supports firmware download to the board FPGA, analog input with optional command mode, optional analog output, 32-bit digital I/O, and optional 8254 counter subdevice.

### Important APIs, Types, And Functions
`struct me4000_board` captures board capabilities and `struct me4000_private` stores PLX base plus AI command timing/control mode. Key functions include `me4000_xilinx_download()`, `me4000_reset()`, `me4000_ai_insn_read()`, `me4000_ai_cancel()`, `me4000_ai_check_chanlist()`, `me4000_ai_round_cmd_args()`, `me4000_ai_do_cmd_test()`, `me4000_ai_do_cmd()`, `me4000_ai_isr()`, `me4000_ao_insn_write()`, DIO handlers, `me4000_auto_attach()`, and `me4000_detach()`.

### Control Flow
Attach selects the board from PCI ID, enables PCI, records PLX BAR1 and device BAR2 I/O bases, loads `me4000_firmware.bin`, resets PLX/AI/AO/DIO state, requests IRQ if available, and creates AI/AO/DIO/counter subdevices. Single AI builds a one-entry channel list, enables FIFOs, triggers through a dummy read, polls data FIFO not empty, reads data, and resets AI. Command mode validates supported trigger combinations, rounds nanoseconds to 33 MHz ticks, checks differential/range constraints, programs timers and sample counter interrupts, writes channel list, and starts acquisition. The ISR drains half-full FIFO blocks or final sample-counter data, flags overflow/error/EOA, and resets interrupt bits.

### State, Persistence, And Dependencies
Persistent state includes firmware-loaded FPGA state, PLX interrupt enable, AI control mode/tick values, AO readbacks, DIO direction/state, optional 8254 pacer, and PCI I/O resources. Dependencies include `plx9052.h`, Comedi firmware loader, Comedi 8254 helpers, shared IRQs, Comedi async buffers, and board-specific timer/FIFO semantics.

### Integration Points
The PCI ID table maps many ME-4650/4660/4670/4680 variants to capability flags. `MODULE_FIRMWARE(ME4000_FIRMWARE)` declares the required FPGA bitstream. IRQ availability controls whether AI command mode is exposed.

### Risks
The driver is marked untested. Firmware download validates a header length but writes bytes with long sleeps and hardware flag checks. `me4000_ai_insn_read()` appears to offset-munge twice via `me4000_ai_get_sample()` and another `comedi_offset_munge()`. Command validation mutates private timing state during `cmdtest`. FIFO state interpretation in the ISR is narrow and can flag undefined states.

### Test Signals
Test firmware missing/bad/success cases, every board capability combination, IRQ and no-IRQ attach, single AI in single-ended/differential modes, command trigger combinations and timer rounding, channel-list validation, FIFO half/full/final interrupts, AO writes, opto-isolated DIO direction rules, 8254 allocation, cancel, and detach interrupt disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/me4000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/me_daq.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/me_daq.c

### Purpose
`me_daq.c` is the Comedi PCI driver for Meilhaus ME-2600i and ME-2000i data acquisition cards. It provides synchronous AI, optional AO, and 32-bit DIO, with firmware download required for ME-2600i.

### Important APIs, Types, And Functions
`struct me_board` describes firmware/AO capabilities; `struct me_private_data` mirrors PLX, control, and DAC control registers. Important functions are `me2600_xilinx_download()`, `me_reset()`, `me_ai_insn_read()`, `me_ao_insn_write()`, `me_dio_insn_config()`, `me_dio_insn_bits()`, `me_auto_attach()`, and `me_detach()`.

### Control Flow
Attach maps PLX BAR0 and board BAR2, downloads `me2600_firmware.bin` when required, resets mirrored control state, then configures AI, optional AO, and DIO subdevices. AI clears/enables channel-list and ADC FIFOs, writes a single chanlist entry with channel/gain/unipolar/differential bits, sets software-trigger mode, starts each conversion by reading control, polls FIFO-not-empty, reads and munges 12-bit data, then disables ADC mode. AO enables DACs, selects buffered mode, updates DAC control for channel range/bipolar mode, writes data registers, and performs an update read. DIO configures port A/B direction in `ctrl2` and reads either state mirrors or hardware based on output direction.

### State, Persistence, And Dependencies
State includes MMIO mappings, firmware-programmed FPGA state, mirrored `ctrl1`, `ctrl2`, and `dac_ctrl`, DIO state/io direction, and AO readback. Dependencies include PLX9052 registers, Comedi PCI/firmware helpers, scheduler timeout sleeps in firmware download, and Comedi munger/range helpers.

### Integration Points
PCI IDs `0x2600` and `0x2000` select ME-2600i or ME-2000i. `MODULE_FIRMWARE(ME2600_FIRMWARE)` declares the ME-2600i firmware dependency. The driver is instruction-only; no IRQ command path is exposed.

### Risks
Firmware download uses second-long sleeps and writes directly through BAR2, so probe can be slow and hardware-specific. `sleep()` wraps `schedule_timeout_interruptible()` without setting task state locally. Register mirrors must remain coherent with hardware after every path. Differential AI validation is limited to channel/range.

### Test Signals
Test firmware success/failure on ME-2600i, ME-2000i attach without firmware, reset mirror values, AI single-ended/differential reads and timeouts, AO range control/readback, DIO port direction transitions, detach reset/unmap, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/me_daq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mf6x4.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/mf6x4.c

### Purpose
`mf6x4.c` is the Comedi PCI driver for Humusoft MF634 and MF624 DAQ cards. It exposes 8-channel AI, 8-channel AO, 8-bit DI, and 8-bit DO using memory-mapped BARs whose hardware numbering differs by board.

### Important APIs, Types, And Functions
`struct mf6x4_board` maps logical BAR0/1/2 to physical PCI BAR numbers. `struct mf6x4_private` stores mapped BAR0, BAR2, and the board-specific GPIOC register pointer. Main callbacks are `mf6x4_ai_insn_read()`, `mf6x4_ao_insn_write()`, `mf6x4_di_insn_bits()`, `mf6x4_do_insn_bits()`, `mf6x4_auto_attach()`, and `mf6x4_detach()`.

### Control Flow
Attach selects the board, enables PCI, maps logical control/data BARs, computes the GPIOC register address, and creates four subdevices. AI writes a one-channel scan mask, triggers conversion by reading ADSTART, waits for the EOLC bit to go low, reads 14-bit data, munges two's-complement to offset binary, and clears ADCTRL. AO enables instantaneous DAC update and DAC outputs in GPIOC, writes samples to the selected DAC register, and updates readback. DIO reads/writes 8-bit values in a shared DIN/DOUT register.

### State, Persistence, And Dependencies
Persistent state is mapped BARs, GPIOC pointer, AO readback, and DO state. Hardware DAC enable/LDAC state persists after writes. Dependencies include Comedi PCI helpers, memory-mapped I/O accessors, Comedi timeouts, and accurate per-board BAR mapping.

### Integration Points
PCI IDs for Humusoft MF634 and MF624 select `bar_nums[]` and GPIOC offset. The driver registers via `module_comedi_pci_driver()`.

### Risks
The macro `MF6X4_ADCTRL_CHAN(x)` expands to `BIT(chan)` rather than `BIT(x)`, relying on a local variable name and making the macro unsafe outside the current function. Attach maps multiple BARs; partial failures rely on later detach paths. No locking protects simultaneous AI/AO/DIO accesses.

### Test Signals
Test both board IDs and BAR maps, GPIOC register selection, AI EOLC timeout and all channels, AO enable/readback, DI/DO bit masks, partial map failure cleanup, and concurrent subdevice operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mf6x4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.c

### Purpose
`mite.c` is a shared Comedi helper for National Instruments MITE PCI interface chips. It maps MITE/DAQ windows, manages DMA channels and rings, prepares DMA descriptors, synchronizes DMA progress with Comedi async buffers, and exports channel lifecycle APIs for NI board drivers.

### Important APIs, Types, And Functions
Public exported APIs include `mite_attach()`, `mite_detach()`, `mite_alloc_ring()`, `mite_free_ring()`, `mite_buf_change()`, `mite_init_ring_descriptors()`, `mite_request_channel_in_range()`, `mite_request_channel()`, `mite_release_channel()`, `mite_prep_dma()`, `mite_dma_arm()`, `mite_dma_disarm()`, `mite_ack_linkc()`, `mite_done()`, `mite_sync_dma()`, and `mite_bytes_in_transit()`. Internal helpers decode chip signature, FIFO size, retry limits, DRQ request lines, byte counters, and status.

### Control Flow
Consumer drivers call `mite_attach()` during auto-attach; it allocates state, initializes channels, maps MITE BAR0 and DAQ BAR1, programs the I/O window, enables a DMA burst register workaround, reads chip signature, resets DMA channels, disables interrupts, and records FIFO size. A driver allocates a ring, lets Comedi buffer changes allocate coherent descriptors, requests a free channel, prepares width/direction/link registers, arms DMA, and services interrupts by acknowledging link-complete/done and syncing buffers. Release aborts/resets DMA, disables all channel interrupts, and frees the channel.

### State, Persistence, And Dependencies
Persistent state includes `struct mite`, per-channel ownership/done flags, coherent descriptor rings, device references, MITE and DAQ MMIO mappings, channel count, FIFO size, and spinlock-protected channel allocation. It depends on PCI bus mastering, DMA coherent memory, Comedi async buffer/page maps, endian conversion for descriptors, and MITE register semantics.

### Integration Points
The file exports GPL symbols for NI Comedi drivers. It is not itself a Comedi device driver but a module-level helper. `mite.h` is the public local contract.

### Risks
DMA accounting uses lower/upper bounds and detects overwrite/underrun by comparing hardware byte counters with Comedi allocation counts; off-by-one or wrap behavior can cause false overflow or data loss. `mite_buf_change()` computes descriptor links from `prealloc_bufsz >> PAGE_SHIFT`, so non-page-sized buffers need scrutiny. DMA release can be called from interrupt context, so lock ordering matters. Window programming differs for `use_win1`.

### Test Signals
Test attach on MITE/minimite variants, channel count clamping, window 0 and window 1 setup, ring allocation/free on buffer resize, input and output DMA sync, finite output regeneration, link-complete/done/error interrupts, channel request/release races, and detach after partial setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.h -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.h

### Purpose
`mite.h` declares the local Comedi MITE DMA helper interface and the small public data structures shared between `mite.c` and NI board drivers.

### Important APIs, Types, And Functions
Core types are `struct mite_dma_desc`, `struct mite_ring`, `struct mite_channel`, and `struct mite`. The header declares all exported helper APIs for ring allocation, descriptor initialization, buffer-change handling, channel request/release, DMA prepare/arm/disarm, interrupt acknowledgement, completion checks, byte-in-transit reporting, attach, and detach. It also defines `MAX_MITE_DMA_CHANNELS` and window register constants `MITE_IODWBSR`, `MITE_IODWBSR_1`, `WENAB`, and `MITE_IODWCR_1`.

### Control Flow
The header has no implementation flow. It encodes the lifecycle expected by callers: attach MITE, allocate ring, respond to Comedi buffer changes, request a DMA channel, prepare and arm it, synchronize/acknowledge interrupts, release the channel, free the ring, and detach.

### State, Persistence, And Dependencies
`struct mite` persists PCI device identity, MITE MMIO mapping, channel array, channel count, FIFO size, and spinlock. Rings persist coherent descriptor memory and a device reference. Channels persist direction, completion, and current ring ownership. The header depends on spinlocks, DMA address types through included kernel headers, and forward declarations for Comedi and PCI types.

### Integration Points
NI Comedi drivers include this header to use `mite.c` without duplicating register details. The constants expose only MITE window registers used externally; most register definitions stay private in `mite.c`.

### Risks
Callers can directly mutate public structs, so ownership and locking conventions are implicit. Descriptor fields are fixed little-endian 32-bit values and assume DMA addresses fit the hardware format. `dir` is an integer expected to match Comedi direction constants.

### Test Signals
Compile all drivers that include `mite.h`, check exported symbol prototypes, exercise channel lifecycle with lockdep, validate descriptor endian layout, and test misuse cases such as release without ring, zero buffer size, and attach failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mpc624.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/mpc624.c

### Purpose
`mpc624.c` is a legacy Comedi driver for the Micro/sys MPC-624 PC/104 board based on an LTC2440 24-bit sigma-delta ADC. It exposes only analog input; DIO, LEDs, EEPROM, and IRQ masking registers are not implemented.

### Important APIs, Types, And Functions
`struct mpc624_private` stores the selected ADC speed/oversampling command. Range tables model two bipolar board ranges. Important functions are `mpc624_ai_get_sample()`, `mpc624_ai_eoc()`, `mpc624_ai_insn_read()`, and `mpc624_attach()`.

### Control Flow
Attach reserves a manually supplied 16-byte I/O region, allocates private state, translates option 1 into an LTC2440 speed/OSR command, creates one four-channel differential AI subdevice, and selects a range table. AI writes the mux/channel selection, toggles ADC chip-select and clock lines to start conversion, waits until busy clears, then bit-bangs 32 serial clock cycles. The returned word is decoded from LTC2440 sign/two's-complement style into an unsigned Comedi sample.

### State, Persistence, And Dependencies
Persistent state is the I/O region and selected `ai_speed`. Hardware state includes mux/channel selection and ADC conversion state. The driver depends on port I/O, microsecond delays, Comedi legacy attach, and Comedi timeout polling.

### Integration Points
The driver registers as a manual Comedi legacy driver via `module_comedi_driver()`. User configuration supplies base address, conversion rate, and voltage range.

### Risks
The attach range-table selection appears to use option 1, although comments describe option 2 as voltage range. The code always writes `insn->chanspec` to the gain/mux/channel port and warns that it always selects the +/-10.1 V range bit behavior. Bit-banged timing and sign conversion are hardware-sensitive.

### Test Signals
Test all speed options, default speed fallback, both intended range options, AI reads on all four channels, timeout when busy remains set, EOC/DMY debug warnings, I/O base validation, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/mpc624.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/multiq3.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/multiq3.c

### Purpose
`multiq3.c` is a legacy Comedi driver for the Quanser MultiQ-3 board. It supports AI, AO, DI, DO, and an optional encoder/counter subdevice with up to eight channels depending on installed encoder chips.

### Important APIs, Types, And Functions
The driver defines the MultiQ-3 register map, encoder commands, `MULTIQ3_MAX_ENC_CHANS`, and callbacks `multiq3_ai_insn_read()`, `multiq3_ao_insn_write()`, `multiq3_di_insn_bits()`, `multiq3_do_insn_bits()`, `multiq3_encoder_insn_read()`, `multiq3_encoder_insn_config()`, `multiq3_encoder_reset()`, `multiq3_attach()`, and helper `multiq3_set_ctrl()`.

### Control Flow
Attach reserves a 16-byte I/O region, allocates five subdevices, configures fixed AI/AO/DI/DO surfaces, sizes the encoder subdevice from option 2 times two capped at eight, and resets each encoder. AI sets control bits with SH/CLK held high, waits for EOC, triggers each conversion, waits for internal EOC, reads two bytes, masks 13-bit data, and offset-munges it. AO selects/load-strobes the channel, writes the sample, clears control, and stores readback. Encoder reads select a channel, reset the byte pointer, latch counter to output latch, read 24 bits, and bias the value so zero maps to midscale.

### State, Persistence, And Dependencies
Persistent state is the I/O reservation, AO readback, DO state, encoder chip configuration, and encoder counter state in hardware. Dependencies include Comedi legacy config, port I/O, Comedi timeout polling, and encoder command semantics.

### Integration Points
Manual configuration supplies base address and optional encoder chip count. Comedi exposes the encoder as `COMEDI_SUBD_COUNTER` with `SDF_LSAMPL`.

### Risks
IRQ option is accepted in documentation but unused. Encoder channel count is derived from user config rather than hardware detection. Control register writes must preserve SH/CLK high. AI conversion sequencing relies on two different EOC bits. Counter overflow is possible after large motion and is only documented in comments.

### Test Signals
Test attach with zero through four encoder chips plus oversized values, AI EOC timeout, AO readback for all channels, DI/DO widths, encoder reset/read/bias behavior, control bit preservation, and I/O base reservation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/multiq3.c -->
