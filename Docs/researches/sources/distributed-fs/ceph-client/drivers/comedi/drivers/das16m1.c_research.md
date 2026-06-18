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
