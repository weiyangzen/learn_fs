# sources/distributed-fs/ceph-client/drivers/gpib/fmh_gpib/fmh_gpib.h

Purpose: defines private state, register offsets, FIFO layout, bit masks, and MMIO helpers for the `fmh_gpib_core` adapter.

Important types and APIs: `struct fmh_priv` embeds `nec7210_priv`, records MMIO resources, IRQ, DMA channel, DMA buffer, burst length, FIFO base, and FIFO interrupt capability. Helpers `fmh_gpib_half_fifo_size`, `gpib_cs_read_byte`, `gpib_cs_write_byte`, `fifos_read`, and `fifos_write` abstract control/status and FIFO register access. Constants define platform and prototype PCI resource indexes, placeholder PCI IDs, extended status registers, ISR/IMR bits, FIFO registers, FIFO control/status flags, data masks, counter masks, and auxiliary commands.

Control flow and state: C code uses `gpib_cs_*` as NEC7210 byte callbacks and `fifos_*` for accelerated PCI/platform FIFO movement. Extended status bits drive `READ_READY_BN`, `WRITE_READY_BN`, `COMMAND_READY_BN`, `RFD_HOLDOFF_BN`, and `RECEIVED_END_BN`. FIFO transfer counters bound chunks to 0x0fff bytes and encode EOI in bit 8 of FIFO data.

Dependencies and integration: includes DMAengine, IO resource, PCI, MMIO, and `nec7210.h`. It is private to `fmh_gpib.c` and assumes hardware register spacing of one byte for control/status and two bytes for FIFO registers, except prototype PCI control/status offset is adjusted in the C file.

Risks: `fmh_gpib_half_fifo_size()` returns the hardware burst length directly; zero would break loops that divide or iterate by half FIFO size if accelerated FIFO paths are used. `fifos_read` returns zero when `fifo_base` is absent, so unsupported FIFO hardware can look like empty/unsupported status unless callers check capabilities. Placeholder PCI IDs must not ship as real IDs.

Test signals: compile-time coverage; unit-style review of bit masks against HDL; hardware tests for FIFO data EOI bit, transfer counter limits, burst length, extended status transitions, RFD holdoff commands, and MMIO spacing on platform versus PCI variants.
