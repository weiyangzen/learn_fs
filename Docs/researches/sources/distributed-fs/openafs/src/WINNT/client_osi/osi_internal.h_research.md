## sources/distributed-fs/openafs/src/WINNT/client_osi/osi_internal.h

Purpose: Supplies debug-build x86 fallbacks for interlocked bitwise AND/OR intrinsics.

Important APIs/functions: Inline `osi_InterlockedAnd` and `osi_InterlockedOr` implement compare-exchange loops using `_InterlockedCompareExchange`; macros alias `_InterlockedAnd`/`_InterlockedOr` to these fallbacks when missing.

Control flow/state: Only active under `DEBUG` and `_M_IX86`. Each loop retries until the compare-exchange observes a stable original value.

Dependencies/integration: Included by `osibasel.c`, which uses `_InterlockedOr` and `_InterlockedAnd` against lock flags.

Risks/tests: Availability differs by compiler/architecture/build mode. Test debug x86 builds with older compiler intrinsics, concurrent flag updates, and non-x86 builds where the fallback is absent.
