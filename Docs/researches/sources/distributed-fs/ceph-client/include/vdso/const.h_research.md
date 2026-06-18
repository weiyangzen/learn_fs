<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/const.h -->
# sources/distributed-fs/ceph-client/include/vdso/const.h

Purpose: exposes minimal typed constant macros for vDSO headers.

Important APIs and types: `UL(x)` and `ULL(x)` wrap `_UL()` and `_ULL()` from `uapi/linux/const.h`.

Control flow: other vDSO macros use these wrappers when building constants that must compile in kernel, user, or assembly-adjacent contexts.

State and persistence: no state.

Dependencies and integration points: depends on UAPI constant helpers and is included by vDSO bit/alignment/page helpers.

Risks and test signals: risks are low; test is broad vDSO compilation in C and assembly contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/const.h -->
