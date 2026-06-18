<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h

**Purpose:** Documents and selects the Alpha per-CPU implementation. Alpha module GP-relative addressing cannot reach kernel per-CPU offsets above 4 GiB, so module per-CPU variables require weak definitions.

**Important APIs/types/functions:** Includes `asm-generic/percpu.h`; architecture behavior is tied to `CONFIG_ARCH_MODULE_NEEDS_WEAK_PER_CPU`.

**Control flow:** No runtime flow. Compile-time configuration changes symbol emission and relocation strategy for module per-CPU variables.

**State and persistence behavior:** Per-CPU state is owned by generic per-CPU infrastructure; this header only constrains module linkage.

**Dependencies and integration points:** Depends on Alpha GCC GP-relative addressing rules, module relocation, and generic per-CPU helpers.

**Risks:** If the Kconfig flag is removed or ignored, module per-CPU references can overflow 32-bit GP displacements.

**Test signals:** Build and load modules declaring per-CPU variables; inspect relocations and run SMP module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/percpu.h -->
