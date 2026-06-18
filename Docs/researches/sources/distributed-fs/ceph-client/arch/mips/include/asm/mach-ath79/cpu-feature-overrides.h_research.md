# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/cpu-feature-overrides.h

**Purpose:** Supplies compile-time CPU feature constants for ATH79 MIPS32 systems so generic MIPS code can optimize away unsupported paths.

**Important APIs/types/functions:** Defines `cpu_has_*` and cache-line macros: TLB, 4K exception/cache, counter, watch, divec, prefetch, EJTAG, LL/SC, MIPS16, MIPS32r1/r2, 32-bit-only GP registers, no FPU/32FPR/64-bit/MIPS MT/userlocal, 32-byte I/D cache lines, D-cache aliases present, and physically indexed D-cache absent. There are no functions or storage declarations.

**Control flow:** The generic MIPS feature machinery includes this header and compiles conditional code based on constant expressions. Runtime flow is affected indirectly because FPU emulation, cache maintenance, exception-vector setup, and LL/SC behavior are selected from these constants.

**State and persistence behavior:** No mutable state. It constrains kernel feature state at compile time and must match real CPU capabilities for every configured ATH79 target.

**Dependencies and integration points:** Integrated by MIPS CPU feature detection and low-level arch code. It must stay consistent with ATH79 CPU revisions and any Kconfig combinations for this machine.

**Risks:** A wrong feature bit can produce invalid instructions, broken cache flushing, missing exception support, or unnecessary slow paths. The file assumes a uniform feature set across ATH79; adding a variant with different MIPS revision/cache/FPU behavior requires revisiting these constants.

**Test signals:** Build ATH79 kernels with CPU feature debug enabled, boot across SoC variants, run cache aliasing stress, LL/SC atomic tests, exception/watchpoint smoke tests, and verify no FPU or 64-bit paths are emitted unexpectedly.
