# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3120.c

## Purpose

This driver supports ADDI-DATA APCI-3120 and APCI-3001 analog input boards. It provides analog input instruction and command support, optional DMA through an AMCC S5933 bridge, optional analog output for APCI-3120, 4-bit DI/DO, and a timer subdevice.

## Important APIs, types, and functions

Key types are `struct apci3120_board`, `struct apci3120_dmabuf`, and `struct apci3120_private`. Important functions include `apci3120_addon_write()`, `apci3120_init_dma()`, `apci3120_setup_dma()`, `apci3120_ns_to_timer()`, timer read/write/mode/enable helpers, `apci3120_set_chanlist()`, `apci3120_interrupt_dma()`, `apci3120_interrupt()`, `apci3120_ai_cmdtest()`, `apci3120_ai_cmd()`, `apci3120_cancel()`, `apci3120_ai_insn_read()`, `apci3120_ao_insn_write()`, DIO handlers, timer `insn_config`, DMA allocation/free, reset, auto-attach, and detach.

## Control Flow

Auto-attach selects board data, allocates private state, enables PCI, sets bus master, records AMCC/add-on/main BARs, resets interrupt/control state, requests an IRQ, allocates coherent DMA buffers when IRQ setup succeeds, detects oscillator base from board revision/status, and allocates AI, AO, DI, DO, and timer subdevices. AI instruction reads set a one-channel chanlist, configure timer 0 for a 10 us software-triggered conversion, poll EOC with `comedi_timeout()`, and read FIFO data. AI commands validate start/scan/convert/stop triggers, program chanlist, optional external trigger, scan and conversion timers, DMA or EOS interrupt mode, then enable acquisition. The ISR handles AMCC DMA completion, EOS PIO sampling, timer2 cleanup, abort diagnostics, finite stop, and COMEDI events.

## State and Persistence

State includes cached `ctrl`, `mode`, timer mode, 4-bit DO state, oscillator base, DMA buffer descriptors, DMA mode flags, current DMA buffer selector, and hardware AMCC/add-on counters. DMA buffers are coherent memory tied to `dev->hw_dev` and freed at detach. No persistent storage is modified.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, AMCC S5933 definitions, DMA coherent allocation, COMEDI async buffers/events, range tables, trigger validation, and readback allocation for AO. It integrates tightly with COMEDI command semantics for finite and continuous AI acquisition.

## Risks

The DMA path is high risk: transfer counts are bytes, sample size is 16 bits, odd byte counts are fatal, and double-buffer sizing changes for `CMDF_WAKE_EOS` and finite stop counts. `apci3120_ai_eoc()` treats EOC bit clear as completion, so polarity must match hardware. Detach calls generic PCI detach before DMA free, but DMA buffers use `dev->hw_dev`; lifetime assumptions should be preserved. Timer divisor rounding and minimum divisor constraints define acquisition timing and can affect user-visible rates.

## Test Signals

Validation should cover APCI-3120 and APCI-3001 probe, revision A/B oscillator timing, single AI reads across ranges/reference modes, command AI with PIO and DMA, finite stop counts, `CMDF_WAKE_EOS`, external trigger gating, AO writes/readback on APCI-3120, 4-bit DIO, timer arm/disarm/mode/status/read, DMA abort logging, cancel quiescing DMA/timers, and coherent buffer cleanup.
