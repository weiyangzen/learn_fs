# subset-b-001196 Comedi DAS/DT driver research

This grouped report covers the requested Comedi DAS08, DAS16, DAS1800/DAS6402/DAS800/DMM32AT, and Data Translation DT28xx source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.c

## Purpose

This is the common DAS08 implementation shared by ISA, PCI, and PCMCIA wrappers. It owns the low-level register protocol for DAS08 analog input, optional analog output, simple digital I/O, optional 8255 DIO, and optional 8254 counter support. Bus-specific files supply a `struct das08_board_struct`; this file turns that metadata into Comedi subdevices.

## Important APIs, types, and functions

Important entry point is exported `das08_common_attach()`. Core handlers are `das08_ai_insn_read()`, `das08_do_insn_bits()`, `das08jr_do_insn_bits()`, `das08_ao_set_data()`, and `das08_ao_insn_write()`. Range and gain tables are selected by `enum das08_lrange` and `enum das08_ai_encoding`. The code uses Comedi helpers `comedi_alloc_subdevices()`, `comedi_timeout()`, `comedi_dio_update_state()`, `subdev_8255_io_init()`, `comedi_8254_io_alloc()`, and `comedi_8254_subdevice_init()`.

## Control Flow, State, and Persistence

Attach stores `dev->iobase`, names the board, allocates six subdevices, and conditionally enables AI, AO, DI, DO, 8255, and 8254 sections. AI reads clear stale ADC bytes, update the mux under `dev->spinlock`, optionally write the per-range gain code, trigger conversion, poll `DAS08_STATUS_AI_BUSY`, and decode 12-bit, PCMCIA 12-bit, or sign-magnitude 16-bit samples. `devpriv->do_mux_bits` persists the shared control-register state because mux and non-JR digital outputs share bits. AO readback persists last values in `s->readback`.

## Dependencies and Integration Points

The file depends on Linux I/O port access, Comedi core, `comedi_8255`, `comedi_8254`, and `das08.h`. It integrates with `das08_isa.c`, `das08_pci.c`, and `das08_cs.c`, which provide resource acquisition and board descriptors before calling `das08_common_attach()`.

## Risks and Test Signals

Risks are shared control-register races, incorrect gainlist/range mapping, 16-bit sign-magnitude interpretation, and AO update semantics differing between JR and AOx boards. Test by loading each bus wrapper, confirming AI conversion values across ranges/channels, toggling DO while AI mux changes, reading DI, checking AO readback/voltage, and verifying optional 8255/8254 subdevices appear only when board metadata requests them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.h

## Purpose

This header is the shared contract between the DAS08 common module and its ISA, PCI, and PCMCIA bus front ends. It defines the board descriptor shape, per-device private state, encoding/range enums, and the common attach function used after each wrapper has claimed its resources.

## Important APIs, Types, and Functions

`enum das08_ai_encoding` describes how the two ADC data registers encode samples: standard 12-bit, 16-bit sign-magnitude, and PCMCIA 12-bit. `enum das08_lrange` selects common AI range/gain tables. `struct das08_board_struct` carries board name, JR flag, AI/AO bit width, AI range and encoding, digital channel counts, 8255/8254 offsets, and I/O size. `struct das08_private_struct` stores the shared DO/mux register shadow and active gainlist. The only exported function prototype is `das08_common_attach()`.

## Control Flow, State, and Persistence

The header has no runtime flow but establishes state ownership. Bus wrappers set `dev->board_ptr` to one of their static board records and allocate `struct das08_private_struct`; `das08_common_attach()` then initializes `pg_gainlist` and maintains `do_mux_bits` at runtime. The fields are in-memory driver state only and are rebuilt on attach.

## Dependencies and Integration Points

It depends only on `linux/types.h` and a forward declaration of `struct comedi_device`, avoiding bus-specific headers. It is included by `das08.c`, `das08_isa.c`, `das08_pci.c`, and `das08_cs.c`.

## Risks and Test Signals

The main risk is descriptor mismatch: a wrong `ai_encoding`, gain enum, offset, or channel count propagates directly into common register programming. Test signals are successful compilation of all wrappers, correct subdevice inventory for each board table entry, and no out-of-range indexing into the common range/gain arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_cs.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_cs.c

## Purpose

This file is the PCMCIA wrapper for the ComputerBoards PCM-DAS08. It handles card matching, PCMCIA resource enablement, private allocation, and then delegates all board operation to the shared DAS08 common code.

## Important APIs, Types, and Functions

The static `das08_cs_boards[]` entry describes a 12-bit PCM-DAS08 with bipolar 5 V AI, PCMCIA sample encoding, 3 DI lines, 3 DO lines, and 16 I/O ports. `das08_cs_auto_attach()` sets `dev->board_ptr`, enables PCMCIA I/O with `comedi_pcmcia_enable()`, allocates `struct das08_private_struct`, and calls `das08_common_attach()`. The PCMCIA integration uses `das08_pcmcia_attach()`, `das08_cs_id_table`, `struct pcmcia_driver`, and `module_comedi_pcmcia_driver()`.

## Control Flow, State, and Persistence

Probe enters through the PCMCIA core, which calls `comedi_pcmcia_auto_config()`. Auto-attach requests automatic I/O assignment with `CONF_AUTO_SET_IO`, reads `link->resource[0]->start` as the base port, and lets common attach create subdevices. Remove uses `comedi_pcmcia_auto_unconfig()` and Comedi detach uses `comedi_pcmcia_disable()`. Runtime state is only the PCMCIA resource, `dev->iobase`, and common DAS08 private state.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pcmcia.h` and `das08.h`. It binds PCMCIA manufacturer/card ID `0x01c5:0x4001` and exports a Comedi driver named `das08_cs` plus a PCMCIA driver named `pcm-das08`.

## Risks and Test Signals

Risks are incorrect PCMCIA ID coverage, failed automatic I/O window assignment, and the special `das08_pcm_encode12` data layout being required for correct samples. Test by inserting a matching card, confirming auto-config creates AI/DI/DO subdevices, reading several AI channels, toggling DO, and checking removal disables the PCMCIA resource cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_isa.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_isa.c

## Purpose

This file is the ISA/PC-104 bus wrapper and board table for many DAS08-family boards. It does not implement I/O behavior directly; it validates and claims the configured I/O port range, allocates common private state, and delegates to `das08_common_attach()`.

## Important APIs, Types, and Functions

`das08_isa_boards[]` describes classic DAS08, PGM/PGH/PGL, AOH/AOL/AOM, JR-AO, JR-16-AO, PC104-DAS08, and DAS08JR/16 variants. Key fields include AI resolution, programmable gain type, AI encoding, AO resolution, digital channel counts, 8255/8254 offsets, JR flag, and I/O size. `das08_isa_attach()` uses `comedi_alloc_devpriv()` and `comedi_check_request_region()`, then calls `das08_common_attach()`. `das08_isa_driver` exposes a legacy Comedi attach interface and board-name table.

## Control Flow, State, and Persistence

The user supplies the base I/O address in option 0. Attach allocates `struct das08_private_struct`, requests the board's port window within ISA limits, and initializes the common subdevices. `comedi_legacy_detach()` releases resources. Board identity is selected by the Comedi board-name mechanism rather than hardware autoprobe.

## Dependencies and Integration Points

Dependencies are Comedi legacy ISA helpers and `das08.h`. Integration points are Comedi's `module_comedi_driver()` registration, user-space `comedi_config`, and the common DAS08 module. Optional 8255/8254 offsets in the table activate shared Comedi helper subdevices.

## Risks and Test Signals

Risks include stale or unchecked `.iosize` values, board-name descriptors not matching physical jumpers, unsupported base address windows, and wrong JR/non-JR register behavior. Test each named board by attach at configured base, verify expected subdevices, check AI encoding and ranges, verify AO where present, and exercise 8254/8255 subdevices for entries with offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_pci.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_pci.c

## Purpose

This file is the PCI wrapper for the ComputerBoards PCI-DAS08. It binds the PCI ID, enables the device, chooses the correct BAR-derived I/O base, allocates common private state, and delegates all board behavior to the shared DAS08 implementation.

## Important APIs, Types, and Functions

`das08_pci_boards[]` describes the PCI-DAS08 as a 12-bit bipolar 5 V AI board with standard DAS08 encoding, 3 DI lines, 4 DO lines, an 8254 at offset 4, and 8 I/O ports. `das08_pci_auto_attach()` allocates `struct das08_private_struct`, sets `dev->board_ptr`, calls `comedi_pci_enable()`, assigns `dev->iobase` from `pci_resource_start(pdev, 2)`, and calls `das08_common_attach()`. `das08_pci_probe()`, `das08_pci_table`, and `module_comedi_pci_driver()` provide PCI binding.

## Control Flow, State, and Persistence

PCI probe calls `comedi_pci_auto_config()`, which invokes auto-attach. The Comedi detach path is `comedi_pci_detach()` and PCI remove is `comedi_pci_auto_unconfig()`. Runtime state is the enabled PCI device, selected I/O BAR, and common DAS08 private state; no persistent configuration is written.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pci.h` and `das08.h`. It integrates with PCI vendor `PCI_VENDOR_ID_CB`, device `0x0029`, the Comedi PCI auto-config framework, and common DAS08 subdevice setup.

## Risks and Test Signals

The primary risks are using the wrong BAR index, failing to handle PCI enable errors, and assuming only one PCI-DAS08 board descriptor. Test with a matching PCI card, verify BAR 2 maps valid I/O registers, confirm AI/DI/DO/8254 subdevices, run AI single reads, and unload/reload to ensure PCI resources are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16.c

## Purpose

This is a legacy ISA Comedi driver for a broad set of DAS16-compatible boards, including DAS-16, DAS-1200/1400/1600, CIO-DAS16, and PC104 variants. It supports polled analog input, optional DMA-backed command acquisition, analog output on capable boards, four-bit DI/DO, optional 8255 DIO, and an 8254 pacer.

## Important APIs, Types, and Functions

Board metadata is in `struct das16_board` and `das16_boards[]`. Runtime state is `struct das16_private_struct`, including ISA DMA, clockbase, control-register shadow, timer, extra I/O region, and burst capability. Key paths are `das16_attach()`, `das16_cmd_test()`, `das16_cmd_exec()`, `das16_interrupt()`, `das16_timer_interrupt()`, `das16_cancel()`, `das16_ai_insn_read()`, `das16_ao_insn_write()`, `das16_ai_range()`, and `das16_detach()`.

## Control Flow, State, and Persistence

Attach validates the optional clock option, claims either a compact I/O range or an additional 0x400 region for DAS1600-style boards, probes ID bits, allocates an 8254 pacer, optionally allocates dual ISA DMA buffers, and creates AI/AO/DI/DO/8255 subdevices. Command execution validates consecutive same-gain chanlists, programs mux/gain and cascaded 8254 timing, sets up DMA, starts a software timer that periodically drains DMA, and enables paced conversion. `ctrl_reg`, timer state, DMA descriptors, and AO readback persist during attach lifetime only.

## Dependencies and Integration Points

The driver depends on Comedi legacy ISA support, `comedi_8254`, `comedi_8255`, `comedi_isadma`, Linux timers, and I/O port access. User options configure base address, DMA channel, master clock, and optional manual AI/AO ranges.

## Risks and Test Signals

Risks include ISA DMA residue handling, command operation without valid DMA being unavailable, burst-mode register differences, ID-bit false negatives, and range polarity inferred from hardware status. Test attach on each board class, run `cmdtest()` edge cases, acquire finite and continuous DMA scans, cancel mid-run, verify timer cleanup, inspect 12/16-bit sample munging, and test base addresses that disable the 8255 at offset 0x10.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16m1.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16m1.c

## Purpose

This driver supports the Measurement Computing CIO-DAS16/M1 ISA board. It provides high-rate 12-bit analog input through a FIFO, interrupt-driven command acquisition without DMA, simple four-bit DI/DO, and an 8255 digital I/O subdevice.

## Important APIs, Types, and Functions

Runtime state is `struct das16m1_private`, holding a secondary 8254 counter, interrupt-control shadow, software ADC count, initial hardware counter value, a 1024-sample buffer, and an extra I/O base. Important functions include `das16m1_ai_set_queue()`, `das16m1_ai_cmdtest()`, `das16m1_ai_cmd()`, `das16m1_handler()`, `das16m1_ai_poll()`, `das16m1_interrupt()`, `das16m1_ai_insn_read()`, `das16m1_irq_bits()`, `das16m1_attach()`, and `das16m1_detach()`.

## Control Flow, State, and Persistence

Attach claims the primary 0x10 I/O region plus an extra region for the 8255/third 8254, optionally requests a valid IRQ, allocates two 8254 blocks, and creates AI, DI, DO, and 8255 subdevices. Command setup programs the channel/range queue, initializes a hardware counter used to estimate FIFO depth, chooses internal or external pacer, optionally enables external start, clears interrupts, and enables IRQs. The handler reads the hardware counter, computes new samples relative to `adc_count`, drains up to FIFO size, detects stop count and overflow, and signals Comedi events.

## Dependencies and Integration Points

The file depends on Linux IRQs, Comedi core, `comedi_8254`, `comedi_8255`, and ISA I/O port allocation. The Comedi command interface is available only if an IRQ is configured.

## Risks and Test Signals

Risks include fragile FIFO-depth calculation before the hardware counter loads, no DMA at high sampling rates, unusual even/odd chanlist restrictions, and limited overrun detection. Test valid and invalid chanlists, internal and external conversion triggers, polling racing with interrupts, stop-count completion, overflow reporting, IRQ mapping for all supported lines, and extra-region release on detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das16m1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das1800.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das1800.c

## Purpose

This is the ISA driver for Keithley DAS-1700/DAS-1800 series boards. It supports many ST, HR, HC, DA, and AO variants with analog input command acquisition via FIFO or ISA DMA, optional analog output on DA models, and simple digital input/output.

## Important APIs, Types, and Functions

Board variants are described by `struct das1800_board` and `das1800_boards[]`. `struct das1800_private` stores DMA state, IRQ/DMA control bits, FIFO buffer, optional second I/O base, and AI polarity. Key routines include `das1800_probe()`, `das1800_attach()`, `das1800_ai_cmdtest()`, `das1800_ai_cmd()`, `das1800_ai_handler()`, `das1800_interrupt()`, `das1800_ai_poll()`, `das1800_ai_set_chanlist()`, `das1800_handle_dma()`, `das1800_ai_cancel()`, and `das1800_detach()`.

## Control Flow, State, and Persistence

Attach claims the base I/O range, probes or verifies model ID from digital-input high bits, optionally claims a second I/O range for waveform AO boards, requests supported IRQs, initializes one or two ISA DMA channels, allocates a FIFO buffer and 8254 pacer, and creates AI/AO/DI/DO subdevices. Commands validate trigger combinations, range polarity consistency, burst timing, and paced timing. Execution configures control A/C bits for start/stop triggers, burst or paced mode, QRAM channel/gain list, 8254 timing, DMA descriptors, and conversion enable. Runtime state lives in hardware registers, DMA descriptors, FIFO buffer, and software control shadows until detach.

## Dependencies and Integration Points

Dependencies are Linux IRQ/I/O APIs, `comedi_8254`, `comedi_isadma`, and Comedi async buffers. User options provide base, IRQ, and up to two DMA channels. The driver integrates with Comedi's legacy attach and command/poll interfaces.

## Risks and Test Signals

Risks include broad model probing ambiguity, unsupported waveform AO despite claiming AO-model resources, external trigger polarity coupling, QRAM indirect-address races, and DMA/FIFO overflow handling. Test finite/continuous AI with FIFO and DMA, burst and paced modes, external start/stop, cancellation flushes, HR 16-bit versus ST 12-bit data paths, DA analog outputs, and cleanup of `iobase2` plus DMA resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das1800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das6402.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das6402.c

## Purpose

This driver supports Keithley Metrabyte DAS6402-12 and DAS6402-16 compatible ISA boards. It provides 64-channel analog input with optional IRQ-driven command acquisition, two-channel analog output, and eight-bit DI/DO.

## Important APIs, Types, and Functions

Board data is `struct das6402_boardinfo`; runtime state is `struct das6402_private` with encoded IRQ and AO range shadow. Key routines include `das6402_reset()`, `das6402_set_mode()`, `das6402_set_extended()`, `das6402_ai_cmdtest()`, `das6402_ai_cmd()`, `das6402_interrupt()`, `das6402_ai_insn_read()`, `das6402_ao_insn_write()`, `das6402_ao_insn_read()`, and `das6402_attach()`.

## Control Flow, State, and Persistence

Attach claims 0x10 ports, resets the board into enhanced mode with 10 MHz pacer clock, optionally requests a valid IRQ, allocates an 8254 pacer, and creates AI/AO/DI/DO subdevices. AI single reads set software trigger mode, range/reference mode, mux low/high to the same channel, clear EOC, trigger conversion, and poll FIFO-not-empty. Commands require timer conversions over a consecutive same-range/same-reference chanlist, program mux low/high, program the pacer, and enable FIFO-not-empty interrupts. AO writes update per-channel range bits and write either left-justified 12-bit words or 16-bit byte pairs.

## Dependencies and Integration Points

Dependencies include Linux IRQs, Comedi core, `comedi_8254`, and I/O port access. It integrates with Comedi async events when an IRQ is configured.

## Risks and Test Signals

There is a likely register typo in the 16-bit AO write path: both byte writes target `DAS6402_AO_LSB_REG(chan)` instead of LSB then MSB. Other risks are enhanced-mode sequencing, differential channel bounds, FIFO overflow, and range bits being ineffective on DAS6402/16. Test polled AI, IRQ command acquisition, 12-bit and 16-bit AO output voltage, XFER-mode AO read-trigger behavior, and valid IRQ remapping for 10/11/15.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das6402.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das800.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das800.c

## Purpose

This driver supports Keithley/Measurement Computing DAS800, DAS801, DAS802, and CIO-DAS802/16 ISA boards. It provides analog input single reads and IRQ-driven command acquisition, plus three digital inputs and four digital outputs.

## Important APIs, Types, and Functions

`struct das800_board` and `das800_boards[]` capture AI speed, range table, and resolution. `struct das800_private` shadows digital-output bits because they share indirect control state. Main functions are `das800_probe()`, `das800_ind_write()`, `das800_ind_read()`, `das800_ai_do_cmdtest()`, `das800_ai_do_cmd()`, `das800_interrupt()`, `das800_ai_insn_read()`, `das800_do_insn_bits()`, and `das800_attach()`.

## Control Flow, State, and Persistence

Attach claims an 8-byte I/O region, probes ID bits through indirect register access, optionally requests IRQs 2-7, allocates a 1 MHz 8254 pacer, and creates AI/DI/DO subdevices. Commands validate consecutive same-gain chanlists, timer or external conversion triggers, and stop mode. Execution disables hardware conversions, programs scan limits and gain, sets conversion-control bits for auto-scan, EOC interrupts, external start, and cascaded timer, then enables card interrupts. The interrupt handler drains samples until FIFO empty, stop count, half FIFO limit, or overflow; CIO-DAS802/16 lacks FIFO-empty status and uses overflow status from the gain register.

## Dependencies and Integration Points

Dependencies are Linux IRQ/delay APIs, Comedi core, and `comedi_8254`. Integration is through legacy Comedi attach and command support gated by IRQ availability.

## Risks and Test Signals

Risks include indirect-register races, gain-code translation differences for 12-bit boards, limited IRQ range, and special FIFO semantics for untested CIO-DAS802/16. Test board probing by ID, AI single reads after mux/gain settling, command scans with internal/external conversion clocks, FIFO overflow reporting, digital output preservation while changing AI mux, and cancellation disabling hardware conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/das800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dmm32at.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dmm32at.c

## Purpose

This driver supports the Diamond Systems Diamond-MM-32-AT board. It provides 32-channel 16-bit analog input, timer/interrupt-driven AI commands, four-channel 12-bit analog output, and a paged 8255 digital I/O subdevice.

## Important APIs, Types, and Functions

Important routines include `dmm32at_reset()`, `dmm32at_ai_set_chanspec()`, `dmm32at_ai_insn_read()`, `dmm32at_ai_cmdtest()`, `dmm32at_setaitimer()`, `dmm32at_ai_cmd()`, `dmm32at_isr()`, `dmm32at_ao_insn_write()`, `dmm32at_8255_io()`, and `dmm32at_attach()`. Range data is in `dmm32at_airanges`, `dmm32at_rangebits[]`, and `dmm32at_aoranges`.

## Control Flow, State, and Persistence

Attach accepts only specific ISA base addresses, claims 0x10 ports, resets and probes readback/status values, optionally requests an IRQ, and creates AI/AO/8255 subdevices. AI setup resets FIFO, optionally enables scan mode, writes low/high channels and range bits, then waits for settling. Command mode validates timer-only scan/convert timing, programs the onboard counters through paged registers under `dev->spinlock`, enables AI interrupts and clock, and the ISR drains one scan into the Comedi buffer. AO writes LSB then MSB/channel, waits for DAC not busy, does a dummy read to update the DAC, and stores readback.

## Dependencies and Integration Points

Dependencies include Linux delay/IRQ, Comedi core, and `comedi_8255`. The 8255 integration uses `subdev_8255_cb_init()` because the DIO registers are behind the board's page register.

## Risks and Test Signals

`dmm32at_reset()` only succeeds when hardware readback indicates all A/D channels are configured single-ended, so jumper settings can block attach. Other risks are page-register races, unsupported external AI triggers despite flags in hardware, coarse conversion timing buckets, and FIFO/status handling. Test supported base addresses, reset probe under jumper variants, AI single and command scans, AO busy timeout/update, 8255 port directions through the callback, and interrupt reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dmm32at.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2801.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2801.c

## Purpose

This driver supports Data Translation DT2801-series and related DT01-EZ boards using a two-port command/data mailbox protocol. It provides synchronous analog input, analog output, and two configurable 8-bit digital I/O ports.

## Important APIs, Types, and Functions

Board identity is represented by `struct dt2801_board` and `boardtypes[]`; private state stores per-channel DAC range tables. Low-level protocol helpers are `dt2801_readdata()`, `dt2801_readdata2()`, `dt2801_writedata()`, `dt2801_writedata2()`, `dt2801_wait_for_ready()`, `dt2801_writecmd()`, `dt2801_reset()`, and `dt2801_error()`. Subdevice handlers include `dt2801_ai_insn_read()`, `dt2801_ao_insn_write()`, `dt2801_dio_insn_bits()`, and `dt2801_dio_insn_config()`.

## Control Flow, State, and Persistence

Attach claims a two-port I/O region, resets the board, reads a board code, maps it to a descriptor, probes AI channel count by issuing `DT_C_READ_ADIM`, allocates four subdevices, and sets range tables from user options. AI reads issue immediate read commands with range and channel bytes and read back a 16-bit value. AO writes issue immediate write commands and update Comedi readback. DIO configuration sends set-input or set-output commands per port; bit operations send write/read digital commands. State is mainly firmware-side mode plus Comedi readback and DIO state.

## Dependencies and Integration Points

Dependencies are Comedi core, Linux delays, and byte I/O. There is no IRQ or DMA command support despite command modifier constants. User options select AI reference/range and DAC ranges.

## Risks and Test Signals

Risks include mailbox timeouts, composite-error recovery via double reset, autoprobe defaulting to type 0 on unknown board code, and `probe_number_of_ai_chans()` causing hardware side effects. Test reset and board-code recognition, AI channel-count probing, AI/AO immediate commands, DIO direction changes on both ports, timeout paths with absent hardware, and range-table selection for each supported board code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2811.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2811.c

## Purpose

This driver supports Data Translation DT2811-PGH and DT2811-PGL ISA boards. It exposes programmable-gain analog input, two-channel analog output, eight-bit DI, eight-bit DO, and optional interrupt-driven AI command acquisition.

## Important APIs, Types, and Functions

Board selection is `struct dt2811_board` with PGH/PGL range table choice. Runtime state is `struct dt2811_private`, storing the encoded AI timer divisor. Important functions are `dt2811_reset()`, `dt2811_ai_read_sample()`, `dt2811_interrupt()`, `dt2811_ai_set_chanspec()`, `dt2811_ai_cmdtest()`, `dt2811_ns_to_timer()`, `dt2811_ai_cmd()`, `dt2811_ai_insn_read()`, `dt2811_ao_insn_write()`, and `dt2811_attach()`.

## Control Flow, State, and Persistence

Attach claims 8 ports, resets ADCSR/data registers, optionally requests IRQs 2/3/5/7, and creates AI/AO/DI/DO subdevices. Single AI reads load channel/gain, which triggers a conversion in mode 0, poll for not busy, and read low/high bytes. Command mode supports start now or external start, timer or external conversion clock, one-channel chanlists, and finite or continuous stop. `cmdtest()` computes the nearest hardware mantissa/exponent timer setting; `cmd()` writes AD mode, timer divisor, and chanspec to arm acquisition. Interrupts write samples and clear AD errors.

## Dependencies and Integration Points

Dependencies are Comedi core, Linux IRQ/delay, and I/O port access. User option 2 selects single-ended, differential, or pseudo-differential channel layout; board name selects PGH/PGL gain table.

## Risks and Test Signals

Risks include nonprogrammable jumper ranges being represented as selectable Comedi ranges, external-clock divisor semantics, one-channel command limitation, and AD error overflow handling. Test all reference modes, PGH/PGL gain choices, timer rounding boundaries, IRQ acquisition with finite stop, external trigger/clock combinations, AO writes/readback, and DIO state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2811.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2814.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2814.c

## Purpose

This driver supports the Data Translation DT2814, a 16-channel 12-bit analog input board with a limited onboard timer. It provides polled single conversions and optional IRQ-driven timed acquisition for one channel.

## Important APIs, Types, and Functions

Important routines are `dt2814_ai_notbusy()`, `dt2814_ai_clear()`, `dt2814_ai_eoc()`, `dt2814_ai_insn_read()`, `dt2814_ns_to_timer()`, `dt2814_ai_cmdtest()`, `dt2814_ai_cmd()`, `dt2814_ai_cancel()`, `dt2814_interrupt()`, `dt2814_attach()`, and `dt2814_detach()`. Register state is controlled through `DT2814_CSR` and two-byte sample reads from `DT2814_DATA`.

## Control Flow, State, and Persistence

Attach claims two I/O ports, clears stale data/errors, optionally requests an IRQ, and creates a single AI subdevice. Polled reads clear stale state, write the channel to CSR to start conversion, wait for `FINISH`, then combine high and low data bytes. Command mode validates `TRIG_TIMER` scan timing, rounds to a power-of-ten timer selector, writes channel plus `ENB` and selector bits, and lets interrupts read samples until error or stop count. Cancel clears `ENB`, noting that doing so triggers an extra conversion that later clear calls mop up.

## Dependencies and Integration Points

Dependencies are Comedi core, Linux IRQ/delay, and I/O port access. Integration is minimal: one AI subdevice and optional `read_subdev` command support if IRQ is configured.

## Risks and Test Signals

Risks include crude timer accuracy, unknown range table, command stop count minimum of two, extra conversion on cancel, and data/error clear requiring two data reads. Test reset clear behavior, polled reads for all channels, IRQ command acquisition, timer rounding, cancel followed by reattach/read, and error flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2814.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2815.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2815.c

## Purpose

This driver supports the Data Translation DT2815 analog output board. It exposes one eight-channel 12-bit AO subdevice with per-channel range tables derived from user configuration for voltage or current output.

## Important APIs, Types, and Functions

`struct dt2815_private` stores per-channel range table pointers and software AO readback. Important routines are `dt2815_ao_status()`, `dt2815_ao_insn_read()`, `dt2815_ao_insn()`, and `dt2815_attach()`. Hardware interaction uses `DT2815_DATA` and `DT2815_STATUS`.

## Control Flow, State, and Persistence

Attach claims two I/O ports, allocates one AO subdevice and private state, assigns each channel either voltage range or current range based on options, rejects absent hardware if status reads `0xff`, resets status, waits up to roughly 100 polling iterations for firmware status `4`, then sends a selected firmware program byte. AO writes wait for status `0x00`, write the low command nibble containing lower data bits/channel/output mode marker, wait for status `0x10`, write upper data bits, and store software readback. There is no hardware readback.

## Dependencies and Integration Points

Dependencies are Comedi core, Linux delay, and I/O port access. Options 2-12 describe board jumper/firmware/output mode choices; IRQ option is explicitly unused.

## Risks and Test Signals

Risks include the file's own untested status, a FIXME that low bit 0 should choose voltage versus current output, slow firmware initialization, hardware detection by floating-bus `0xff`, and no validation that options match physical jumpers. Test attach timing/status sequence, every firmware program option, voltage/current channels, AO write/readback consistency, absent-hardware detection, and output measurements for configured ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2817.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2817.c

## Purpose

This is a simple Comedi driver for the Data Translation DT2817 digital I/O board. It exposes one 32-channel DIO subdevice organized as four independently configurable 8-bit banks.

## Important APIs, Types, and Functions

The driver uses two register offsets: `DT2817_CR` for output-enable control and `DT2817_DATA` as the base of four data bytes. Core routines are `dt2817_dio_insn_config()`, `dt2817_dio_insn_bits()`, and `dt2817_attach()`.

## Control Flow, State, and Persistence

Attach claims five I/O ports, allocates one DIO subdevice, initializes `s->state` to zero, and writes zero to the control register so all banks start as inputs. Config computes the 8-bit bank mask from the requested channel, delegates state update to `comedi_dio_insn_config()`, converts `s->io_bits` into four output-enable bits, and writes the control register. Bit operations write only changed banks and then read all four bytes back into `data[1]`. Direction and output state persist in `s->io_bits`, `s->state`, and hardware registers until detach/reset.

## Dependencies and Integration Points

Dependencies are only Comedi core and I/O port access. It integrates as a legacy Comedi driver named `dt2817`; user option 0 supplies the base address.

## Risks and Test Signals

Risks are low but include bank-granularity direction surprises, writes to input-configured banks depending on hardware behavior, and base alignment constraints. Test configuring each bank input/output, mixed-direction bit updates, readback across all 32 lines, initial all-input state, and attach failure on conflicting I/O regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt2817.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt282x.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt282x.c

## Purpose

This driver supports the Data Translation DT2821-series family, including DT2821/23/24/25/27/28/29 and EZ variants. It provides AI single reads and DMA-backed AI commands, optional AO single writes and DMA-backed AO commands, and 16-bit DIO split into two configurable byte lanes.

## Important APIs, Types, and Functions

Board data is `struct dt282x_board` and `boardtypes[]`; runtime state is `struct dt282x_private`, storing ISA DMA, data-format flag, timer divisor, software AD/DAC/SUP CSR shadows, trigger/read counts, and DMA direction. Key routines are `dt282x_initialize()`, `dt282x_alloc_dma()`, `dt282x_ns_to_timer()`, `dt282x_load_changain()`, `dt282x_ai_insn_read()`, `dt282x_ai_cmdtest()`, `dt282x_ai_cmd()`, `dt282x_ai_dma_interrupt()`, `dt282x_ao_insn_write()`, `dt282x_ao_cmdtest()`, `dt282x_ao_cmd()`, `dt282x_ao_inttrig()`, `dt282x_ao_dma_interrupt()`, `dt282x_interrupt()`, and DIO config/bit handlers.

## Control Flow, State, and Persistence

Attach claims a 16-byte window on a 32-byte boundary, verifies reset register signatures, allocates private state, optionally requests IRQ plus two ISA DMA channels, and creates AI/AO/DIO subdevices according to board capabilities. AI commands program timer, supervisor source, DMA descriptors, channel-gain list, AD clock/interrupt bits, mux preload, and software or external trigger. DMA interrupts alternate buffers, munge two's-complement data when configured, update counters, and signal EOA. AO command mode similarly uses DMA write buffers, an internal trigger callback, DAC clocking, and shared supervisor state. CSR shadows are critical persistent runtime state.

## Dependencies and Integration Points

Dependencies include Linux IRQ/I/O/delay, Comedi core, and `comedi_isadma`. User options define IRQ, two DMA channels, SE/DI jumper state, AI two's-complement format, and jumper-selected range tables.

## Risks and Test Signals

The file warns that simultaneous AI and AO commands can break because they share DMA/supervisor state without arbitration. Other risks are strict DMA channel requirements, register-signature probe false negatives, timer rounding, AO command underruns, and data-format/range jumper mismatch. Test attach signatures, AI/AO single operations, DMA finite acquisitions, AO streaming after internal trigger, cancellation of both directions, DIO direction preservation in `dacsr`, and rejection or documentation of simultaneous command use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/dt282x.c -->
