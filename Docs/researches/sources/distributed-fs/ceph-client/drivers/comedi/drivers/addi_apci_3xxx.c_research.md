# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_3xxx.c

## Purpose

This broad ADDI-DATA driver supports many APCI-3000/3002/3003/3006/3010/3016/3100/3106/3110/3116/3500 variants. It exposes variant-dependent AI, AO, isolated DI/DO, and 24-channel TTL DIO subdevices using PCI I/O and MMIO resources.

## Important APIs, types, and functions

The large `apci3xxx_boardtypes[]` table describes names, AI channel counts, resolution, supported conversion time units, minimum acquisition times, and optional AO/DIO features. Main functions include `apci3xxx_irq_handler()`, `apci3xxx_ai_started()`, `apci3xxx_ai_setup()`, `apci3xxx_ai_insn_read()`, `apci3xxx_ai_ns_to_timer()`, `apci3xxx_ai_cmdtest()`, `apci3xxx_ai_cmd()`, `apci3xxx_ao_insn_write()`, isolated DI/DO handlers, TTL DIO config/bits handlers, `apci3xxx_reset()`, `apci3xxx_auto_attach()`, and `apci3xxx_detach()`.

## Control Flow

PCI auto-attach selects board data, allocates private state, enables PCI, records BAR 2 as port I/O and maps BAR 3 as MMIO, optionally requests an IRQ, computes how many subdevices are required for the variant, and initializes each supported function in order. AI instruction reads call `apci3xxx_ai_setup()` for a single channel, start conversion, poll EOS, and read FIFO data. Command AI support is limited to a single channel with timer conversion and IRQ completion despite comments that hardware supports more scan modes. The IRQ handler checks a status bit, clears it, writes one sample from the FIFO, sets EOA, and handles events.

## State and Persistence

State consists of `ai_timer` and `ai_time_base` cached during command validation, AO readback arrays, DIO `state` and `io_bits`, MMIO/I/O mappings, and hardware FIFO/status/config registers. Reset disables IRQ around clearing start, interrupt flags, EOS, and FIFO entries. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, MMIO accessors, COMEDI trigger validation, timeout polling, readback allocation, and DIO helpers. It binds many ADDI PCI IDs to table entries and uses board metadata rather than per-device code paths.

## Risks

The broad board table is the primary correctness surface: wrong feature flags or timing units create incorrect subdevices or invalid acquisition timing. `apci3xxx_ai_ns_to_timer()` stores `*ns = timer * time_base`, which uses the enum value rather than the nanosecond base and appears suspicious for command argument fixup. `apci3xxx_reset()` disables and enables `dev->irq` even if no IRQ was assigned, so no-IRQ paths need scrutiny. AI command support is intentionally limited and may not match hardware capabilities.

## Test Signals

Testing should include representative variants with and without AI/AO/DIO, AI single reads across range/reference settings, AI command timing validation and IRQ completion, AO writes/readback, isolated DI/DO reads/writes, TTL fixed input/output/programmed port behavior, reset with and without IRQ, and each PCI ID selecting the expected subdevice layout.
