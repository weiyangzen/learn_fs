## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hisi-phase.c

### Purpose
`clk-hisi-phase.c` implements a simple phase-adjustable HiSilicon clock type. It maps a finite set of phase degrees to hardware register values and exposes `.get_phase` and `.set_phase` CCF operations.

### Important APIs, Types, And Functions
`struct clk_hisi_phase` stores register address, masks, shift, phase-degree table, phase-register-value table, count, and lock. `hisi_phase_regval_to_degrees()` and `hisi_phase_degrees_to_regval()` translate values. `hisi_clk_get_phase()` and `hisi_clk_set_phase()` implement ops. `clk_register_hisi_phase()` constructs and registers the clock.

### Control Flow
Registration builds `clk_init_data`, computes the shifted mask, stores the caller-provided mapping arrays, and calls `devm_clk_register()`. Reads mask and shift the register field, then search the table. Writes validate the requested degree, take the shared spinlock, update only the phase field, and release the lock.

### State, Persistence, And Dependencies
The selected phase persists in hardware MMIO. Driver state is devm-managed and references mapping arrays supplied by SoC-specific tables. It depends on CCF phase APIs, `readl`/`writel`, and the caller-provided lock.

### Integration Points
SoC CRG drivers, notably Hi3798CV200 MMC sample/drive clocks, use `hisi_clk_register_phase()` from `clk.c` to expose phase control to MMC and other timing-sensitive consumers.

### Risks
Only exact phase degrees in the mapping table are accepted. The code assumes `lock` is non-NULL in `set_phase()`. Invalid hardware register values return `-EINVAL` on get. Mapping-array lifetime must outlive the registered clock.

### Test Signals
Exercise all listed phases through CCF, verify register values and readback degrees, test rejection of unsupported degrees, and run MMC tuning paths that change sample/drive phases.
