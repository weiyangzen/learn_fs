## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_gicv3.h

### Purpose
Provides ARM64 GICv3 system-register and redistributor/ITS MMIO accessors, including erratum-aware interrupt acknowledge handling and priority masking helpers.

### Important APIs, Types, And Functions
Important helpers include `read_gicreg`, `write_gicreg`, `gic_write_dir`, `gic_read_iar_common`, `gic_read_iar_cavium_thunderx`, `gic_read_iar`, `gic_write_ctlr`, `gic_read_ctlr`, `gic_write_grpen1`, `gic_write_sgi1r`, `gic_read_sre`, `gic_write_sre`, `gic_write_pmr`, `gic_read_pmr`, `gic_flush_dcache_to_poc`, and ITS/GICR read/write macros.

### Control Flow
Inline accessors read and write ICC system registers with required `isb()`, `dsb()`, or memory barriers. `gic_read_iar()` dynamically selects the Cavium ThunderX workaround using alternatives. Priority masking helpers manipulate PMR or DAIF based on system capability.

### State, Persistence, And Dependencies
State is in GIC CPU interface registers and MMIO redistributor/ITS tables. Dependencies include sysreg definitions, GIC common constants, barrier/cacheflush helpers, CPU capability alternatives, and relaxed MMIO accessors.

### Integration Points
Used by the GICv3 irqchip driver, interrupt entry/exit, SGI delivery, ITS setup, and priority-mask based interrupt disabling.

### Risks
Missing barriers can lose or reorder interrupts. Erratum selection must be correct for ThunderX. Relaxed MMIO accessors require callers to add ordering where necessary. PMR masking must align with irqflags semantics.

### Test Signals
Boot GICv3 systems, run interrupt storm and CPU hotplug tests, SGI/IPI tests, ITS/MSI tests, ThunderX erratum coverage, priority masking lockdep/irqsoff tests, and virtualization interrupt tests.
