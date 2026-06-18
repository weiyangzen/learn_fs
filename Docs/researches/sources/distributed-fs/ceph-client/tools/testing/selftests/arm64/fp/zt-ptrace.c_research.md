<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c

Purpose: ptrace ABI selftest for SME2 ZT0 register state and its interaction with ZA enablement.

Important APIs and functions: `get_za`/`set_za` access `NT_ARM_ZA`; `get_zt`/`set_zt` access `NT_ARM_ZT`; tests are `ptrace_za_disabled_read_zt`, `ptrace_set_get_zt`, and `ptrace_enable_za_via_zt`.

Control flow: skip if SME2 unsupported, read current SME VL, fork traced child, wait for SIGSTOP, disable ZA and confirm ZT reads zero, write/read ZT and compare bytes, then disable ZA, write ZT, read ZA header/data to verify ZA became enabled with same VL and expected backing data state.

State and persistence: process-local traced child register state and stack buffers. No files.

Dependencies and integration: uses SME2 HWCAP, `ZT_SIG_REG_BYTES`, ZA sizing macros, ptrace regsets, and kselftest.

Risks: in `ptrace_enable_za_via_zt`, the comment says ZA register data should be non-zero but the loop marks any non-zero byte as failure; this inconsistency needs scrutiny against the intended ABI. It also assumes writing ZT implies PSTATE.ZA-visible ZA data.

Test signals: three TAP tests report disabled read, set/get ZT, and ZA enable via ZT behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/zt-ptrace.c -->
