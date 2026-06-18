# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.c

## Purpose
`nic.c` implements generic NIC support shared by Falcon-architecture devices: coherent DMA buffer allocation, event and IRQ self-test triggers, interrupt request/free logic, ethtool register dump layout and collection, and generic hardware statistic description/update helpers.

## Important APIs, Types, And Functions
`ef4_nic_alloc_buffer()` and `ef4_nic_free_buffer()` allocate/free coherent DMA memory for interrupt status, statistics, and similar fixed buffers. `ef4_nic_event_present()`, `ef4_nic_event_test_start()`, and `ef4_nic_irq_test_start()` support self-tests. `ef4_nic_init_interrupt()` and `ef4_nic_fini_interrupt()` hook and unhook legacy, MSI, or MSI-X handlers, with optional RFS CPU-rmap setup. Register dump support is driven by `struct ef4_nic_reg`, `struct ef4_nic_reg_table`, `ef4_nic_regs[]`, and `ef4_nic_reg_tables[]`, with `ef4_nic_get_regs_len()` computing size and `ef4_nic_get_regs()` reading the selected registers/tables. Statistics helpers are `ef4_nic_describe_stats()` and `ef4_nic_update_stats()`.

## Control Flow
Interrupt initialization chooses legacy if MSI is not in use, otherwise optionally allocates an RX CPU rmap for MSI-X and requests one IRQ per channel. Failures unwind already-requested IRQs and free the rmap. Register dump functions filter register and table definitions by `efx->type->revision`; table reads switch on stride to choose 32-bit MMIO/SRAM, 64-bit SRAM, 128-bit table, or interleaved 128-bit table access. Stat updates iterate a mask and convert little-endian 16/32/64-bit DMA fields into `u64` values, either replacing or accumulating.

## State And Persistence
DMA buffer helpers persist kernel virtual and DMA addresses in `struct ef4_buffer`. Interrupt setup persists IRQ registrations and `net_dev->rx_cpu_rmap`. Self-tests write `event_test_cpu` and `last_irq_cpu` with memory barriers before requesting hardware-generated test signals. Register dumps are snapshots of hardware state, not persistent driver state. Stat helpers update caller-owned `u64` arrays.

## Dependencies And Integration Points
This file depends on Linux DMA, interrupt, PCI, module, seq/cpu-rmap APIs, local `net_driver.h`, `bitfield.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, and workaround definitions. It integrates directly with the hardware vtable for IRQ handlers and test generation, with `io.h` for register access, with ethtool register/stat APIs, and with RFS acceleration support.

## Risks
IRQ setup has several partial-failure paths where cleanup order matters. Register dump arrays must avoid write-only or read-clear registers; comments mark many exclusions but future additions could accidentally disturb hardware. The register dump buffer is advanced as a `void *`, relying on compiler support. `ef4_nic_update_stats()` trusts descriptor offsets and DMA widths; a mismatched descriptor can read the wrong DMA buffer bytes or silently report zero after `WARN_ON`.

## Test Signals
Signals include successful IRQ request/free across legacy, MSI, and MSI-X modes, RFS CPU-rmap creation, self-test interrupts/events arriving on recorded CPUs, ethtool `get_regs` length matching the emitted dump, stable register dumps on each supported revision, and correct ethtool statistic names and values from 16/32/64-bit DMA fields.
