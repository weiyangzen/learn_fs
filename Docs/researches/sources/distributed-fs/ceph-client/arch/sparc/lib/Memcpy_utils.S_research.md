# sources/distributed-fs/ceph-client/arch/sparc/lib/Memcpy_utils.S

Purpose: Shared SPARC64 exception-return helpers for copy/memcpy implementations, especially CPU-specific user-copy variants.

Important APIs/functions: Defines `__restore_asi_fp`, `__restore_asi`, and many `memcpy_retl_*` helpers that compute residual byte counts from registers such as `%o2`, `%o3`, `%o4`, `%o5`, and `%g1`.

Control flow: Helpers branch to ASI restore paths, optionally execute `VISExitHalf`, restore `%asi` to `ASI_AIUS`, calculate the value returned in `%o0`, and return. FP-suffixed helpers restore VIS/FPU state before returning.

State and persistence: No persistent state; restores transient `%asi` and FPU state after exceptional or partial copy paths.

Dependencies/integration: Includes `linux/linkage.h`, `asm/asi.h`, and `asm/visasm.h`. Used by M7, NG4, and similar copy engines through exception-table fixup targets.

Risks/test signals: Residual arithmetic must match the exact faulting copy stage. Test page-fault injection at many byte offsets, verify `%asi` restoration after faults, and run VIS/FPU state preservation checks.
