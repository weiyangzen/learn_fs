<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h

**Purpose:** Overrides `READ_ONCE` on Alpha SMP to include a full memory barrier after volatile loads, covering Alpha implementations that can reorder address-dependent loads.

**Important APIs/types/functions:** `__READ_ONCE(x)` under `CONFIG_SMP`, then generic `rwonce` definitions.

**Control flow:** On SMP, `READ_ONCE` expands to a volatile scalar load followed by `mb()` before returning the value; UP builds use generic behavior.

**State and persistence behavior:** No state; it defines memory-ordering semantics used throughout the kernel.

**Dependencies and integration points:** Depends on `asm/barrier.h`, generic `rwonce`, and Alpha's memory model.

**Risks:** Removing the barrier can break RCU and lockless algorithms that rely on address dependencies on other architectures. Overuse costs performance but preserves correctness.

**Test signals:** RCU torture, LKMM litmus tests for Alpha, lockless list/hash tests, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/rwonce.h -->
