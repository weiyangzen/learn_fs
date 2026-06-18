# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc_asm.h

Purpose: adapts kernel powerpc assembly naming and feature macros for userspace selftest builds.

Important APIs/types/functions: maps `_GLOBAL()` and `_GLOBAL_TOC()` to `FUNC_START(test_...)`, defines `CONFIG_ALTIVEC`, register aliases, stack offsets, and no-op feature-section macros.

Control flow: no executable logic; it shapes symbol names and assembly preprocessing.

State and persistence behavior: no state.

Dependencies and integration points: includes `<ppc-asm.h>` from the tools environment and is consumed by imported kernel-style assembly implementations.

Risks and test signals: no-op feature sections mean code guarded for CPU features may assemble unconditionally in the test context, so C tests must perform hardware capability skips where needed.
