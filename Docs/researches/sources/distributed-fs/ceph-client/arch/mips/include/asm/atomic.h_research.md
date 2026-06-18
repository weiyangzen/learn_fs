<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h

**Purpose:** Implements MIPS architecture atomic integer operations.

**Important APIs/types/functions:** Defines `arch_atomic_read/set`, arithmetic and bitwise operations, relaxed return/fetch variants, 64-bit variants under `CONFIG_64BIT`, and `arch_atomic_sub_if_positive`/`dec_if_positive`.

**Control flow:** If LL/SC is unavailable, operations disable local IRQs and update memory directly. Otherwise inline assembly loops with `ll/sc` or `lld/scd`, sync barriers, and `SC_BEQZ` retry until store succeeds.

**State, dependencies, integration:** Relies on `kernel_uses_llsc`, sync/barrier macros, compiler asm constraints, and Loongson3 workarounds. Used throughout kernel refcounts/counters.

**Risks and test signals:** Memory ordering is subtle; some operations are relaxed while others add explicit barriers. Test atomic litmus cases on SMP, 32/64-bit builds, no-LLSC fallback, Loongson workaround configs, and `sub_if_positive` negative path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h -->
