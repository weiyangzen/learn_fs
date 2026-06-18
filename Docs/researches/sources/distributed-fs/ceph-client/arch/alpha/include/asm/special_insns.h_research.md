<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h

**Purpose:** Wraps Alpha special instructions for implementation version and architectural mask probing.

**Important APIs/types/functions:** `enum implver_enum`, `implver()`, `enum amask_enum`, and `amask(mask)`.

**Control flow:** Generic kernels emit `implver` at runtime; CPU-specific builds fold it to constants. `amask` returns unsupported feature bits for the supplied mask.

**State and persistence behavior:** No state; it reads CPU architectural feature state.

**Dependencies and integration points:** Depends on Alpha assembler support and config options such as `CONFIG_ALPHA_GENERIC`, `CONFIG_ALPHA_EV56`, and `CONFIG_ALPHA_EV6`.

**Risks:** Compile-time constant folding must match the actual CPU target. Misinterpreting `amask` can enable unsupported instructions.

**Test signals:** Boot generic and CPU-specific kernels, compare detected features with `/proc/cpuinfo`, and run instruction-alternative paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/special_insns.h -->
