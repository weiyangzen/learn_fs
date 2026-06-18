<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/const.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/const.h

Purpose: this vDSO helper exposes typed constant macros `UL()` and `ULL()` backed by the UAPI Linux constant helpers.

Important APIs/types: `UL(x)` expands to `_UL(x)`, and `ULL(x)` expands to `_ULL(x)`. The included `uapi/linux/const.h` handles details such as assembler vs C constant spelling.

Control flow: compile-time only.

State and persistence: no state.

Dependencies/integration: used by `vdso/bits.h` and other low-level headers that need literal suffixes to be portable across toolchains.

Risks and test signals: test with C and assembler preprocessing where these headers are included. Main risk is suffix mismatch causing truncation or invalid assembly tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/const.h -->
