# subset-b-001203 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.c

### Purpose
`ni_tio.c` is the shared Comedi support library for National Instruments general-purpose counters used by board drivers such as `ni_660x` and `ni_pcimio`. It translates Comedi counter configuration requests into NI STC/TIO register programming for E-series, M-series, and 660x variants, and exposes exported helpers for counter construction, initialization, routing, instruction reads/writes, arming, and gate/clock setup.

### Important APIs, Types, And Functions
The file operates on `struct ni_gpct` and `struct ni_gpct_device` declared in `ni_tio.h`. Exported APIs include `ni_tio_write()`, `ni_tio_read()`, `ni_tio_set_bits()`, `ni_tio_get_soft_copy()`, `ni_tio_arm()`, `ni_tio_set_gate_src()`, `ni_tio_set_gate_src_raw()`, `ni_tio_insn_config()`, `ni_tio_insn_read()`, `ni_tio_insn_write()`, `ni_tio_init_counter()`, `ni_tio_get_routing()`, `ni_tio_set_routing()`, `ni_tio_unset_routing()`, `ni_gpct_device_construct()`, and `ni_gpct_device_destroy()`. Internal helpers handle variant-specific clock codes, gate selectors, second-gate support, source subselects, ABZ encoder source registers, sync mode, and load-register selection.

### Control Flow, State, And Persistence
`ni_gpct_device_construct()` allocates a counter device, per-counter array, and per-chip software register cache. Each counter records `chip_index`, `counter_index`, `clock_period_ps`, and a spinlock for later DMA association. Register writes flow through caller-provided board callbacks, while `ni_tio_set_bits()` updates the cached register image under `regs_lock` before writing hardware. Counter setup resets/disarms, clears auto-increment, mode, load, input, counting mode, second-gate, DMA, and interrupt registers. `ni_tio_insn_config()` dispatches Comedi instruction requests for counter mode, arm/disarm/status, clock source get/set, gate source get/set, other ABZ source set, and reset. Read/write instructions access current count through `SW_SAVE`, cached Load A/B registers, and transient `GI_LOAD` operations.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Comedi counter constants, NI route naming conventions, board-supplied register I/O callbacks, and NI routing tables. It is tightly integrated with `ni_tiocmd.c`, which uses its gate, arm, DMA, and interrupt helpers. Risks include stale software register cache if board callbacks bypass this layer, variant-specific selector translation errors, undocumented M-series second-gate raw pass-through, unsafe current-count writes while armed, and ambiguous clock periods for external sources. Test signals include setting/getting clock sources with prescale and inversion, gate and gate2 raw and generic routing, ABZ source routing, counter arm modes, load-register reads/writes, reset state, invalid destination handling in routing helpers, and concurrency around `regs_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.h -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.h

### Purpose
`ni_tio.h` is the public header for the NI general-purpose counter support layer. It defines the register namespace, hardware variant enum, core counter/device state structures, and exported APIs consumed by NI Comedi board drivers.

### Important APIs, Types, And Functions
Important definitions are `enum ni_gpct_register`, `enum ni_gpct_variant`, `struct ni_gpct`, and `struct ni_gpct_device`. `struct ni_gpct_device` holds board callback hooks `write` and `read`, the variant, counter array, register cache, `regs_lock`, and route tables. Public functions include constructor/destructor helpers, counter initialization, Comedi instruction callbacks, command/cancel/interrupt helpers, MITE channel binding, interrupt acknowledge, and route get/set/unset helpers.

### Control Flow, State, And Persistence
The header does not execute logic, but it defines the persistent shape used by `ni_tio.c` and `ni_tiocmd.c`. The software register cache is stored as `[num_chips][NITIO_NUM_REGS]` and protected by `regs_lock`; each counter stores its MITE DMA channel pointer under its own lock. Callers create a `ni_gpct_device`, initialize counters, attach individual `struct ni_gpct` instances to Comedi subdevices, and then reuse the function table for synchronous instructions or asynchronous commands.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `linux/comedi/comedidev.h` and forward declarations from NI routing/MITE users. Integration is through exported symbols in `ni_tio.c` and `ni_tiocmd.c`. Risks are ABI-style coupling: register enum ordering is assumed by cache arrays and register-index macros, and callback users must honor the locking/cache model. Test signals include building all NI counter consumers, constructing devices with different counter counts/chip groupings, and verifying command-capable drivers can bind `mite_channel` without including private internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio_internal.h -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio_internal.h

### Purpose
`ni_tio_internal.h` provides the private NI TIO register-offset macros, bit definitions, and internal helper prototypes shared by `ni_tio.c` and `ni_tiocmd.c`.

### Important APIs, Types, And Functions
It defines per-counter register index macros such as `NITIO_CMD_REG(x)`, `NITIO_MODE_REG(x)`, `NITIO_INPUT_SEL_REG(x)`, `NITIO_CNT_MODE_REG(x)`, `NITIO_GATE2_REG(x)`, `NITIO_SHARED_STATUS_REG(x)`, `NITIO_DMA_CFG_REG(x)`, `NITIO_INT_ACK_REG(x)`, and `NITIO_INT_ENA_REG(x)`. Bit macros cover arm/disarm/load, gating modes, edge behavior, stop/output/reload modes, source/gate selectors, counter modes, prescale and alternate sync, DMA enable/status, interrupt acknowledgments, and status/error indicators. The inline `ni_tio_counting_mode_registers_present()` distinguishes E-series from M-series/660x hardware.

### Control Flow, State, And Persistence
The header centralizes the bit layout that both synchronous counter configuration and asynchronous command support use. State persistence comes indirectly through the register-cache APIs declared here: `ni_tio_set_bits()`, `ni_tio_get_soft_copy()`, `ni_tio_arm()`, `ni_tio_set_gate_src()`, and `ni_tio_set_gate_src_raw()`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ni_tio.h` for register enums and structures. Integration risk is high because wrong bit definitions affect hardware programming across all NI counter users. Special care is needed for per-counter shared-status bit calculations, variant-specific prescale/alt-sync bits, and gate interrupt acknowledge/confirm bits. Test signals include compile-time coverage of both `ni_tio.c` and `ni_tiocmd.c`, counter status/error reporting, DMA interrupt acknowledge behavior, and E-series paths that lack counting-mode and gate2 registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tiocmd.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tiocmd.c

### Purpose
`ni_tiocmd.c` adds asynchronous Comedi command support for NI general-purpose counters, intentionally split from `ni_tio.c` so the base counter library does not depend directly on the MITE DMA module.

### Important APIs, Types, And Functions
Exported APIs are `ni_tio_cmd()`, `ni_tio_cmdtest()`, `ni_tio_cancel()`, `ni_tio_acknowledge()`, `ni_tio_handle_interrupt()`, and `ni_tio_set_mite_channel()`. Internal helpers include `ni_tio_configure_dma()`, `ni_tio_input_inttrig()`, `ni_tio_input_cmd()`, `ni_tio_output_cmd()`, `ni_tio_cmd_setup()`, `should_ack_gate()`, and `ni_tio_acknowledge_and_confirm()`.

### Control Flow, State, And Persistence
`ni_tio_cmdtest()` validates Comedi trigger combinations: start can be now/internal/other and optionally external on hardware with counting-mode registers; scan or convert may use external gate sources; stop is unsupported beyond `TRIG_NONE`. `ni_tio_cmd()` requires a bound MITE channel, configures an external gate if requested, enables gate interrupts for `CMDF_WAKE_EOS`, then starts input DMA or rejects output commands as unsupported. Input setup allocates the full buffer, prepares DMA width by variant, configures read acknowledge/interrupt bits, arms DMA immediately or installs an internal trigger callback. Cancellation disarms the counter, disarms DMA, disables DMA register bits, and clears gate interrupt enable.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `ni_tio_internal.h`, `mite.h`, and `ni_routes.h`. It integrates with board interrupt handlers that call `ni_tio_handle_interrupt()` and with callers that assign DMA channels through `ni_tio_set_mite_channel()`. Risks include no interrupt-only command path, unsupported output commands, E-series gate-ack behavior depending on DMA completion, commented-out external start-trigger validation, and ordering between MITE DMA arm/disarm and counter arm. Test signals include command validation steps, `TRIG_INT` start, external gate routing by raw and named routes, DMA overflow/DRQ error callbacks, gate/TC error reporting, `CMDF_WAKE_EOS`, and cancel while DMA is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tiocmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_usb6501.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_usb6501.c

### Purpose
`ni_usb6501.c` is a USB Comedi driver for the National Instruments USB-6501, exposing 24 digital I/O channels and one 32-bit counter through reverse-engineered bulk USB command packets.

### Important APIs, Types, And Functions
Important state is `struct ni6501_private`, which stores RX/TX endpoint descriptors, a mutex, and shared USB buffers. Core helpers are `ni6501_port_command()` and `ni6501_counter_command()`. Comedi callbacks include `ni6501_dio_insn_config()`, `ni6501_dio_insn_bits()`, `ni6501_cnt_insn_config()`, `ni6501_cnt_insn_read()`, and `ni6501_cnt_insn_write()`. USB/Comedi lifecycle functions are `ni6501_find_endpoints()`, `ni6501_alloc_usb_buffers()`, `ni6501_auto_attach()`, `ni6501_detach()`, `ni6501_usb_probe()`, and `comedi_usb_auto_unconfig`.

### Control Flow, State, And Persistence
Attach allocates private data, records it on the USB interface, validates exactly two bulk endpoints with sufficient max packet size, allocates endpoint-sized buffers, and creates DIO and counter subdevices. All device transactions are synchronous two-packet USB exchanges: prepare a template request, send it to the bulk OUT endpoint, read a template response from bulk IN, mask variable data fields, and compare the response header. DIO config updates Comedi `io_bits` and sends one direction packet for all three ports; bit operations write changed ports and then read all ports. Counter config starts, stops, or resets by stopping and writing zero; reads/writes convert big-endian 32-bit counter payloads.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `linux/comedi/comedi_usb.h`, USB bulk helpers, Comedi DIO helpers, and the USB ID table `{0x3923, 0x718a}`. Risks include strict response-template matching across firmware versions, shared buffer lifetime under disconnect, synchronous USB timeouts, endian/unaligned `__be32` casts in packet buffers, and no asynchronous interrupt support. Test signals include endpoint validation failures, repeated DIO read/write/config operations, counter arm/disarm/reset/read/write, disconnect during blocked USB I/O, and invalid response packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_usb6501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl711.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl711.c

### Purpose
`pcl711.c` supports Advantech PCL-711/PCL-711B and ADLink ACL-8112 compatible ISA data-acquisition boards with analog input, analog output, digital input/output, optional IRQ-driven AI commands, and an 8254 pacer.

### Important APIs, Types, And Functions
Board-specific data lives in `struct pcl711_board`, including AI/AO channel counts, IRQ ceiling, minimum I/O base, and AI ranges. Key callbacks are `pcl711_ai_insn_read()`, `pcl711_ai_cmdtest()`, `pcl711_ai_cmd()`, `pcl711_ai_cancel()`, `pcl711_interrupt()`, `pcl711_ao_insn_write()`, `pcl711_di_insn_bits()`, `pcl711_do_insn_bits()`, and `pcl711_attach()`.

### Control Flow, State, And Persistence
Attach reserves 16 I/O ports, optionally requests an IRQ, allocates a 2 MHz 8254 pacer, and creates four subdevices. Synchronous AI selects gain and channel/MPC508 mux, enters software-trigger mode, pulses the soft-trigger register, waits for DRDY, and reads a 12-bit sample. Command-mode AI supports one-channel scan lists with timer or external scan triggers and IRQ delivery; the interrupt reads one sample, clears the status latch, writes to the Comedi buffer, and signals EOA for finite acquisitions. AO writes store readback and program LSB/MSB registers; DO state persists in `s->state`.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Comedi legacy attach, `comedi_8254`, port I/O, and Linux IRQ APIs. Risks include unrequested IRQ silently disabling command support, PCL-711B IRQ bits in the mode register differing from jumper-based boards, range/gain settling assumptions, `MAX_SPEED` minimum conversion timing, and fixed one-entry command channel list. Test signals include polled AI on all board types/ranges, timer and external IRQ command paths, cancel disabling pacer and clearing status, AO readback allocation, DIO state updates, and attach behavior with invalid IRQ or I/O base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl724.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl724.c

### Purpose
`pcl724.c` is a compact 8255-based digital I/O driver for several ISA/PC-104 boards, including PCL-724, PCL-722, PCL-731, ACL-712x, PET-48DIO, PCM-IO48, and ONYX-MM-DIO.

### Important APIs, Types, And Functions
`struct pcl724_board` describes I/O range, valid address limits, optional 96-channel mode, PET-48 special mapping, and the number of 8255 subdevices. Main functions are `pcl724_8255mapped_io()` for PET-48 indirect-style mapping and `pcl724_attach()` for resource reservation and subdevice setup.

### Control Flow, State, And Persistence
Attach selects the requested I/O span and number of 8255 instances, with PCL-722/ACL-7122 able to reduce from 144 to 96 DIO channels. It reserves the I/O region and creates one Comedi subdevice per 8255 chip. Normal boards use `subdev_8255_io_init()` at consecutive 8255 offsets; PET-48 uses `subdev_8255_cb_init()` with a callback that derives a moved port number from the high bits of the encoded I/O base.

### Dependencies, Integration Points, Risks, And Test Signals
The driver delegates most behavior to `comedi_8255`. It does not implement IRQ support even though config option 1 is documented as unsupported. Risks include incorrect board table I/O spans, unusual PET-48 port mapping, and 96/144-channel option ambiguity. Test signals include subdevice counts and channel counts for each board, 96-channel mode for PCL-722/ACL-7122, PET-48 callback reads/writes, and attach rejection for out-of-range bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl726.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl726.c

### Purpose
`pcl726.c` supports Advantech PCL-726/PCL-727/PCL-728 and ADLink ACL-6126/ACL-6128 D/A and optional DIO boards, including optional external-trigger interrupt reporting for ACL-6126-class hardware.

### Important APIs, Types, And Functions
`struct pcl726_board` captures I/O length, minimum I/O base, supported IRQ mask, AO range tables, AO channel count, DIO presence, and PCL-727 register layout. `struct pcl726_private` stores per-channel AO range tables and `cmd_running`. Key callbacks are `pcl726_ao_insn_write()`, `pcl726_di_insn_bits()`, `pcl726_do_insn_bits()`, `pcl726_intr_cmdtest()`, `pcl726_intr_cmd()`, `pcl726_intr_cancel()`, `pcl726_interrupt()`, and `pcl726_attach()`.

### Control Flow, State, And Persistence
Attach reserves the board I/O region, optionally requests a supported IRQ, maps configuration options into a per-channel `range_table_list`, and allocates AO, optional DI/DO, and optional interrupt DI subdevices. AO writes convert bipolar values to DAC two's-complement format, write MSB then LSB, and persist user values in Comedi readback. DIO operations use different register offsets for PCL-727 versus other boards. The interrupt command path is simple: a valid external trigger sets `cmd_running`, the ISR writes a zero sample and completes the command, and cancel clears the flag.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi legacy ISA resource management and IRQ APIs. Risks include incorrect per-channel range options producing `range_unknown`, write-order sensitivity for DAC programming, PCL-727 alternate DI/DO offsets, and minimal interrupt samples without actual edge data. Test signals include AO range selection by config option, bipolar munge correctness, DIO register offset differences, unsupported IRQ ignored behavior, one-sample external trigger command completion, and readback consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl726.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl730.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl730.c

### Purpose
`pcl730.c` implements digital input/output support for many Advantech, ADLink, ICP, Diamond Systems, and WinSystems boards with varying isolated and TTL DIO register maps. Interrupts and some auxiliary timer/change-detect registers are intentionally unsupported.

### Important APIs, Types, And Functions
`struct pcl730_board` describes I/O range/alignment, special layouts (`is_pcl725`, `is_acl7225b`, `is_ir104`), readback support, TTL support, subdevice count, and channel counts. Core callbacks are `pcl730_do_insn_bits()`, `pcl730_di_insn_bits()`, `pcl730_get_bits()`, and `pcl730_attach()`.

### Control Flow, State, And Persistence
Attach validates special IR104 base addresses, reserves the requested I/O region with board-specific alignment, and creates subdevices for isolated DO, isolated DI, optional TTL DO, and optional TTL DI. Register offsets are stored in `s->private` so the generic bit handlers can read or write the right byte group. DO state persists in `s->state`, optionally initialized from hardware on boards with readback. Reads aggregate up to four bytes depending on channel count; writes emit only byte lanes touched by the Comedi mask.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on simple port I/O and Comedi DIO state helpers. Risks include table-driven layout errors across many boards, unsupported control/interrupt features on boards that physically have them, readback availability differences, and channel counts not byte-multiple on IR104's 20-bit banks. Test signals include per-board subdevice layout, byte-lane masked writes, readback initialization, IR104 allowed base validation, and TTL versus isolated bank offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl730.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl812.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl812.c

### Purpose
`pcl812.c` is a broad Comedi driver for Advantech PCL-812/PCL-813, ADLink ACL-811x/8216, and ICP DAS A-821/A-822/A-823/A-826/ISO-813 analog acquisition boards. It supports synchronous AI, optional IRQ/DMA command AI, AO, and DIO depending on board capabilities.

### Important APIs, Types, And Functions
Important structures are `struct pcl812_board` and `struct pcl812_private`. Main AI helpers include `pcl812_ai_set_chan_range()`, `pcl812_ai_eoc()`, `pcl812_ai_cmdtest()`, `pcl812_ai_cmd()`, `pcl812_handle_eoc()`, `pcl812_handle_dma()`, `pcl812_ai_poll()`, `pcl812_ai_cancel()`, and `pcl812_ai_insn_read()`. Other callbacks include `pcl812_ao_insn_write()`, `pcl812_di_insn_bits()`, `pcl812_do_insn_bits()`, `pcl812_reset()`, `pcl812_set_ai_range_table()`, DMA allocation/free helpers, attach, and detach.

### Control Flow, State, And Persistence
Attach allocates private state, reserves 16 I/O ports, conditionally creates an 8254 pacer and IRQ, optionally allocates two 8 KiB ISA DMA buffers, applies differential/external-trigger options, and creates AI/AO/DIO subdevices based on board features. AI command validation supports `TRIG_NOW` start, `TRIG_FOLLOW` scans, timer or external conversion, and finite or continuous stop. Command start sets the first channel/range, decides whether DMA can be used only for repeated single-channel scans, honors `CMDF_WAKE_EOS`, programs DMA and/or the pacer, and enables hardware trigger mode. Interrupt handling either transfers DMA buffers or reads one EOC sample, advances scans, clears status, and handles events. Reset disables triggers, clears status, initializes channel/range, zeros AO, and clears digital outputs.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `comedi_8254`, `comedi_isadma`, ISA port I/O, IRQ handling, Comedi buffers, and board option tables. Risks include many board-specific range tables and option indexes, DMA limited to single-channel scans, external-trigger mode selected at attach time, gain settling fixed with small delays, range-correction offsets for ISO/ACL variants, and command support disappearing without IRQ. Test signals include polled AI for 12/16-bit boards, timer and external command validation, DMA and IRQ-only acquisition, poll path partial DMA transfer, finite stop EOA, cancel cleanup, differential mux selection, AO range options, DIO state writes, and attach cleanup with invalid DMA/IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl812.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl816.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl816.c

### Purpose
`pcl816.c` supports Advantech PCL-816 and PCL-814B analog input boards with DMA-backed command acquisition, synchronous AI reads, and basic DI/DO subdevices. Despite hardware AO presence on some boards, AO is not implemented.

### Important APIs, Types, And Functions
`struct pcl816_board` records AI resolution and channel-list length, while `struct pcl816_private` stores ISA DMA state, polling pointer, and command running/canceled flags. Important functions are `pcl816_ai_setup_dma()`, `pcl816_ai_setup_chanlist()`, `pcl816_interrupt()`, `check_channel_list()`, `pcl816_ai_cmdtest()`, `pcl816_ai_cmd()`, `pcl816_ai_poll()`, `pcl816_ai_cancel()`, `pcl816_ai_insn_read()`, DIO callbacks, `pcl816_alloc_irq_and_dma()`, attach, and detach.

### Control Flow, State, And Persistence
Attach reserves 16 ports, tries to allocate a valid IRQ 2-7 plus DMA channel 1 or 3, creates a 10 MHz 8254 pacer, and allocates four subdevices. Command support is enabled only if IRQ/DMA setup succeeded. Command validation requires continuous/repeating channel lists that match the board scan hardware, timer or external conversion, and finite or continuous stop. Starting a command programs the channel/range scan segment, marks the command running, programs the first DMA buffer, configures pacer mode, enables DMA/interrupt trigger mode, and writes the selected DMA/IRQ values to status. ISR and poll paths move DMA samples to the Comedi buffer and track `ai_poll_ptr`; cancel disables control/pacer and marks a canceled interrupt state.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Comedi ISA DMA, 8254 pacer helpers, IRQ APIs, and port I/O. Risks include command code assuming DMA is present once command callbacks are exposed, channel-list continuity constraints, cancellation races handled by `ai_cmd_canceled`, unused piggyback subdevice, and hard-coded 10 us minimum timer validation. Test signals include invalid channel-list rejection, command start busy checks, timer and external trigger modes, DMA interrupt and poll transfer, cancel before/after interrupt, synchronous AI timeout handling, and DI/DO byte state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl816.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl818.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl818.c

### Purpose
`pcl818.c` supports Advantech PCL-818/PCL-718/PCM-3718 boards with synchronous AI, IRQ/DMA/FIFO command AI, AO, DI, and DO. It handles single-ended or differential AI detection and optional FIFO support on HD/HG variants.

### Important APIs, Types, And Functions
`struct pcl818_board` captures minimum sample period, AO channels, AI range table, DMA/FIFO presence, and 818-family flag. `struct pcl818_private` stores DMA, selected sample period, active channel list segment/position, FIFO usage, and command running/canceled flags. Key functions are `pcl818_ai_setup_dma()`, `pcl818_ai_setup_chanlist()`, `pcl818_ai_get_sample()`, `pcl818_ai_get_fifo_sample()`, `pcl818_ai_write_sample()`, `pcl818_handle_eoc()`, `pcl818_handle_dma()`, `pcl818_handle_fifo()`, `pcl818_interrupt()`, `check_channel_list()`, `ai_cmdtest()`, `pcl818_ai_cmd()`, `pcl818_ai_cancel()`, `pcl818_ai_insn_read()`, AO/DIO callbacks, reset, range selection, DMA helpers, attach, and detach.

### Control Flow, State, And Persistence
Attach reserves either 0x10 or 0x20 ports depending on FIFO support/base address, requests IRQ 2-7, optionally enables FIFO or allocates DMA channel 1/3, creates a 1 MHz or 10 MHz 8254 pacer, selects AI range tables from jumpers/options, and configures four subdevices. AI command setup validates repeating continuous channel sequences, stores the hardware scan segment, marks the command running, selects timer or external trigger, then enables DMA, FIFO, or interrupt-only acquisition. ISR dispatches to DMA/FIFO/EOC handlers, each checking channel tags against the expected scan position before buffering samples. Cancel may defer DMA teardown until a final interrupt when a transfer is active, then disables trigger, pacer, and FIFO.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi ISA DMA, 8254, IRQs, port I/O, and Comedi buffers. Risks include untested FIFO code, FIFO availability tied to base address/JP6, channel dropout detection triggering errors, deferred DMA cancel ordering, no `poll` callback despite DMA, detected single-ended mode from status bit, and board option overlap between AI and AO ranges. Test signals include single-ended/differential detection, command validation for channel-list continuity, timer and external triggers, DMA and FIFO ISR paths, channel tag mismatch error, cancel during DMA, finite stop EOA, AO nibble-shift register writes, and reset disabling FIFO/pacer/outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcl818.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcm3724.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcm3724.c

### Purpose
`pcm3724.c` supports the Advantech PCM-3724 48-channel digital I/O board built from two 8255 devices plus extra direction and gate-control registers for 74HCT245 line buffers.

### Important APIs, Types, And Functions
`struct priv_pcm3724` tracks which channels have been enabled on each 8255 bank. Important helpers are `compute_buffer()`, `do_3724_config()`, `enable_chan()`, `subdev_3724_insn_config()`, and `pcm3724_attach()`.

### Control Flow, State, And Persistence
Attach reserves 16 I/O ports, allocates two 8255 subdevices, initializes each with `subdev_8255_io_init()`, and replaces the normal config callback. Channel config updates Comedi `io_bits` by byte group, computes the external buffer direction register for both 8255 chips, writes the 8255 control word, and enables the channel's gate-control bit. Direction and enable state persist in the 8255 subdevice `io_bits` and private `dio_1`/`dio_2` masks.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `comedi_8255`, Comedi DIO config helpers, and legacy ISA I/O resources. Risks include mismatched 8255 direction convention versus external buffer direction bits, the channel 16-19/20-23 split for port C halves, and gate-enable masks only increasing as channels are configured. Test signals include configuring each A/B/C port on both 8255s, verifying buffer direction register values, gate enable updates, normal 8255 bit reads/writes after overridden config, and attach failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcm3724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmad.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmad.c

### Purpose
`pcmad.c` is a simple synchronous analog-input driver for Winsystems PCM-A/D12 and PCM-A/D16 boards, with board-configured single-ended/differential reference and straight-binary or bipolar two's-complement encoding.

### Important APIs, Types, And Functions
`struct pcmad_board_struct` selects 12-bit or 16-bit maximum data. Main functions are `pcmad_ai_eoc()`, `pcmad_ai_insn_read()`, and `pcmad_attach()`.

### Control Flow, State, And Persistence
Attach reserves four I/O ports and creates one AI subdevice. Configuration options select 16 single-ended or 8 differential channels and unipolar 0-5 V or bipolar +/-10 V range. Each read writes the channel number to the convert register, waits until status bits 0 and 1 are both set, reads LSB/MSB, shifts 12-bit board data down by four bits, munges bipolar two's-complement values into Comedi offset-binary form, and returns the requested number of samples. The driver has no persistent runtime state beyond board selection and subdevice configuration.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi timeout helpers and port I/O. Risks include a likely documentation/option mismatch because comments name option 2/3 while attach checks options 1/2, no IRQ support despite an unused IRQ option in the comments, hardware jumper mismatch not detectable by software, and tight polling-only behavior. Test signals include 12-bit and 16-bit sample formatting, single-ended versus differential channel counts, bipolar munge, timeout on missing EOC bits, and I/O region alignment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmda12.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmda12.c

### Purpose
`pcmda12.c` supports the Winsystems PCM-D/A-12, an 8-channel 12-bit analog-output PC/104 board with jumper-selected output ranges and optional simultaneous-transfer mode.

### Important APIs, Types, And Functions
`struct pcmda12_private` stores `simultaneous_xfer_mode`. Main callbacks are `pcmda12_ao_insn_write()`, `pcmda12_ao_insn_read()`, `pcmda12_ao_reset()`, and `pcmda12_attach()`.

### Control Flow, State, And Persistence
Attach reserves 16 I/O ports on a 32-byte boundary, stores the simultaneous-transfer option, creates one readable/writable AO subdevice, allocates readback, and resets all channels to zero. Writes program channel-specific LSB/MSB registers and either immediately latch by reading an AO register or, in simultaneous mode, leave data preloaded until a later AO read triggers transfer for all channels. Readback is maintained in `s->readback`, while hardware latch timing depends on the selected transfer mode.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi readback helpers and port I/O. Risks include range values being advisory because physical jumpers determine output range, simultaneous mode requiring reads to latch values, no command support, and alignment assumptions from the datasheet. Test signals include immediate and simultaneous write modes, read-triggered latch, reset zeroing every channel, readback correctness, and invalid base rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmda12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmmio.c -->
## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmmio.c

### Purpose
`pcmmio.c` supports the WinSystems PCM-MIO PC/104 multifunction board: 16-channel 16-bit AI, 8-channel 16-bit AO, and two 24-channel DIO banks, with edge-detect interrupt command support on the first DIO bank.

### Important APIs, Types, And Functions
`struct pcmmio_private` holds a page-register spinlock, command-state spinlock, enabled interrupt mask, and active flag. Important helpers include `pcmmio_dio_write()`, `pcmmio_dio_read()`, `pcmmio_dio_insn_bits()`, `pcmmio_dio_insn_config()`, `pcmmio_reset()`, `pcmmio_start_intr()`, `pcmmio_stop_intr()`, `interrupt_pcmmio()`, `pcmmio_handle_dio_intr()`, `pcmmio_cmdtest()`, `pcmmio_cmd()`, `pcmmio_cancel()`, `pcmmio_ai_insn_read()`, `pcmmio_ao_insn_write()`, and `pcmmio_attach()`.

### Control Flow, State, And Persistence
Attach reserves 32 I/O ports, initializes locks, resets DIO ports and paged interrupt registers, optionally requests and routes an IRQ, then creates AI, AO, interrupt-capable DIO, and plain DIO subdevices. DIO port/page access is serialized because the WS16C48 uses a shared page selector. DIO outputs are inverted/open-drain style; writes invert `s->state` and mask inputs high-Z, while reads invert hardware bits back to logical values. DIO commands support `TRIG_NOW` or `TRIG_INT` start, external scan begin, one packed sample per interrupt, finite or continuous stop, and per-channel edge polarity encoded from range/aref bits. AI reads issue a command to one of two LTC1859 ADCs, perform a dummy conversion because results lag one command, then collect samples and munge bipolar data. AO writes program LTC2704 span first, then write/update code for the selected DAC/channel and store readback.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi legacy resources, IRQ handling, spinlocks, port I/O, and Comedi buffers. Risks include a typo-like `PCMMIO_PAGE_MASK` macro referencing `PCMUIO_PAGE`, untested interrupt support, paged register races if any path bypasses `pagelock`, open-drain DIO polarity confusion, AI dummy-conversion sequencing, and AO subdevice marked readable without an `insn_read` callback. Test signals include AI reads across both ADC chips/ranges, AO range and code writes across both DACs, DIO input/output config and inversion, interrupt polarity/channel-list masks, `TRIG_INT` start, pending interrupt clear, cancel disabling page-enable bits, and reset clearing all paged registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmmio.c -->
