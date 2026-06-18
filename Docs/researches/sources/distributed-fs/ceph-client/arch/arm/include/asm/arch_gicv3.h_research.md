<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h

## Purpose
ARM32 architecture-specific GICv3 system-register and MMIO accessor layer used by the generic irqchip GICv3 driver.

## Important APIs/types/functions
- CP15 register aliases for ICC registers: `ICC_EOIR1`, `ICC_DIR`, `ICC_IAR1`, `ICC_SGI1R`, `ICC_PMR`, `ICC_CTLR`, `ICC_SRE`, `ICC_IGRPEN1`, `ICC_BPR1`, `ICC_RPR`, AP registers.
- `CPUIF_MAP()` creates AArch64-style read/write wrappers for selected ICC registers.
- Low-level helpers: `gic_read_iar()`, `gic_write_dir()`, `gic_write_ctlr()`, `gic_write_grpen1()`, `gic_write_sgi1r()`, SRE/PMR/BPR/RPR accessors.
- Non-atomic 64-bit MMIO helpers for IROUTER, BASER, PROPBASER, PENDBASER, and ITS registers.
- ARM32 stubs for priority masking: `gic_prio_masking_enabled()` false and warning stubs for PMR masking.

## Control flow
Inline functions translate generic GIC driver operations into ARM32 CP15 `read_sysreg/write_sysreg` or ordered 32-bit MMIO pairs. Some writes issue `isb()` and interrupt acknowledge issues `dsb(sy)`.

## State and persistence behavior
State is hardware interrupt-controller state: ICC CPU interface registers, distributor/redistributor/ITS MMIO registers, and dcache flush side effects. The header itself stores no data.

## Dependencies and integration points
Depends on ARM CP15 accessors, IO helpers, cache flush, barriers, and GIC register definitions. Used by the GICv3 irqchip driver when built for AArch32.

## Risks and edge cases
64-bit accesses are deliberately non-atomic; comments document when that is safe. `gicr_write_vpendbaser()` must clear Valid before changing fields. Calling PMR masking stubs on ARM32 warns because that feature is unsupported here.

## Test signals
Boot ARM32 GICv3 platforms, exercise interrupts, SGIs, LPIs/ITS if available, CPU hotplug, and virtualization pending-table paths. Run irqchip selftests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h -->
