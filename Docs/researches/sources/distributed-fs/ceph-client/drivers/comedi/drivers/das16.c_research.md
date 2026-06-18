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
