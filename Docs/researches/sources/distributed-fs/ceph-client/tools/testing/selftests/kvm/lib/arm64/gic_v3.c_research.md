# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3.c

## Purpose
This file implements guest-side GICv3 register programming for arm64 selftests, including distributor, redistributor, CPU interface, interrupt state controls, and LPIs for ITS-backed tests.

## Important APIs, Types, and Functions
Key internals include `struct gicv3_data`, `gicv3_gicd_wait_for_rwp()`, `gicv3_gicr_wait_for_rwp()`, `get_intid_range()`, `gicv3_access_reg()`, and register read/write helpers. Publicly consumed exports include `gicv3_ops`, `gicv3_reg_readl()`, `gicv3_reg_writel()`, and `gic_rdist_enable_lpis()`.

## Control Flow
`gicv3_init()` records CPU and SPI counts, caps SPIs at 1020, and initializes the distributor. `gicv3_dist_init()` disables the distributor, resets SPI group/active/enable/priority registers, then enables Group-1 with affinity routing. `gicv3_cpu_init()` validates redistributor CPU numbering, wakes the redistributor, resets SGI/PPI state, enables ICC system-register access, sets priority mask, and enables Group-1 interrupts.

## State, Dependencies, and Integration
The static `gicv3_data` records guest-visible GIC capacity. All MMIO accesses target fixed guest virtual bases from `gic_v3.h`, which host setup maps in `vgic.c`. The implementation uses arm64 sysreg accessors, memory barriers, `udelay()`, and KVM selftest asserts.

## Risks and Test Signals
Register write-pending waits can assert if emulation never clears RWP. The code assumes sequential redistributor layout and `GICR_TYPER.Processor_number == cpu`. Test failures surface as guest asserts, interrupt delivery errors, or timeouts in RWP loops.
