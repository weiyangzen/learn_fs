# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/amx.c

## Purpose

`amx.c` validates userspace AMX XTILEDATA xstate behavior on x86_64. It checks that XTILEDATA permission is denied before a sufficiently large signal stack is installed, that `ARCH_REQ_XCOMP_PERM` updates permissions correctly, that permission and compatible altstack state survive fork, that tile data is not inherited across fork, and then delegates to generic xstate context/signal/ptrace tests for XTILEDATA.

## Important APIs, Types, and Functions

The file depends on `xstate.h` helpers such as `alloc_xbuf()`, `clear_xstate_header()`, `set_xstatebv()`, `set_rand_data()`, `xrstor()`, `xsave()`, `get_fpx_sw_bytes()`, `get_fpx_sw_bytes_features()`, `get_xstate_info()`, and `test_xstate()`. It uses `arch_prctl` codes `ARCH_GET_XCOMP_SUPP`, `ARCH_GET_XCOMP_PERM`, and `ARCH_REQ_XCOMP_PERM`. Important local functions are `handle_noperm()`, `xrstor_safe()`, `load_rand_tiledata()`, `validate_req_xcomp_perm()`, `validate_xcomp_perm()`, `test_dynamic_sigaltstack()`, `test_dynamic_state()`, `validate_tiledata_regs_changed()`, and `test_fork()`.

## Control Flow

`main()` skips unless `ARCH_GET_XCOMP_SUPP` advertises tile config and tile data. It obtains XTILEDATA size/offset, allocates a stashed XSAVE buffer, and installs a SIGILL handler. `test_dynamic_state()` forks so permission experiments cannot contaminate later tests; the child confirms XTILEDATA load fails without permission, installs a small altstack and expects permission request failure, installs a large altstack and expects success, rejects later shrinking below the AMX requirement, confirms XTILEDATA can load, and validates inheritance in a grandchild. Back in the original process, `main()` requests XTILEDATA permission, runs `test_fork()` to confirm child tile registers differ from parent-loaded tile data, then calls generic `test_xstate(XFEATURE_XTILEDATA)`.

## State and Persistence Behavior

State is process-local xstate, signal-handler state, altstack mappings, and forked process state. There is no file persistence. The test deliberately changes the process's dynamic xstate permission and signal stack configuration.

## Dependencies and Integration Points

It requires x86_64, CPU and kernel AMX support, dynamic xstate permission support, valid `AT_MINSIGSTKSZ`, signal frame xstate metadata, and the local xstate selftest library. It integrates with kselftest skip/pass/fail conventions through `helpers.h`/`kselftest`.

## Risks and Edge Cases

The SIGILL handler advances RIP by three bytes to skip the expected `XRSTOR`; this depends on the emitted instruction length. Signal-safe output is avoided with a static buffer, but test diagnostics still depend on handler sequencing. If `AT_MINSIGSTKSZ` is absent, sigaltstack-specific coverage is skipped. Forking isolates some permission changes but complicates failure attribution.

## Test Signals

Pass signals include expected SIGILL/`ILL_ILLOPC` before permission, valid signal xstate size/mask without XTILEDATA, failed permission on too-small altstack, successful permission on large altstack, failure to shrink altstack afterward, inherited permission in the grandchild, changed XTILEDATA after fork, and successful generic xstate tests.
