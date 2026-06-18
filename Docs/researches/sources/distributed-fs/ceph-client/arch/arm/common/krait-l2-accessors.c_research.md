<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c

## Purpose
Exports serialized indirect accessors for Qualcomm Krait L2 cache controller registers accessed through CP15 selector/data registers.

## Important APIs/types/functions
- `krait_set_l2_indirect_reg(u32 addr, u32 val)`
- `krait_get_l2_indirect_reg(u32 addr)`
- Global `raw_spinlock_t krait_l2_lock`
- CP15 operations: write selector `c15,c0,6`, write/read data `c15,c0,7`, with `isb()` ordering.

## Control flow
Both functions take the raw spinlock with IRQ save, select the indirect register address, issue an ISB, access the data register, and release the lock.

## State and persistence behavior
State is in hardware L2 registers; the only software state is the lock. Writes persist until hardware reset or later writes by other code.

## Dependencies and integration points
Depends on Krait-specific CP15 register behavior, ARM barriers, raw spinlocks, and callers in Krait cache/SoC support code.

## Risks and edge cases
Using these helpers on non-Krait CPUs would access implementation-defined CP15 registers. Missing serialization can corrupt selector/data transactions, so all indirect accesses must go through these helpers.

## Test signals
Build Krait platforms with `CONFIG_KRAIT_L2_ACCESSORS`; exercise cache/L2 setup paths on hardware and verify no concurrent indirect register corruption under SMP load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c -->
