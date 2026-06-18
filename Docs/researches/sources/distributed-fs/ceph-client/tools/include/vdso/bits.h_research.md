<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/bits.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/bits.h

Purpose: this tiny vDSO helper defines `BIT()` and `BIT_ULL()` using vDSO constant-suffix helpers.

Important APIs/types: `BIT(nr)` expands to `UL(1) << nr`; `BIT_ULL(nr)` expands to `ULL(1) << nr`. These macros create unsigned long or unsigned long long bit masks without hard-coding suffixes directly.

Control flow: compile-time macro expansion only.

State and persistence: no state.

Dependencies/integration: includes `vdso/const.h`, which wraps UAPI constant helpers. Used by vDSO and low-level headers needing bit constants in C and assembler-friendly contexts.

Risks and test signals: risks are shift overflow or using a bit index wider than the target type. Test by compiling masks in 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/bits.h -->
