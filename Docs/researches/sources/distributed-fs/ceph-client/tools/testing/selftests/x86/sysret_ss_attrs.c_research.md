<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c

## Purpose

`sysret_ss_attrs.c` verifies that x86 SYSRET returns with usable hidden SS descriptor attributes, especially on AMD systems where SYSRET can otherwise leave the cached SS descriptor unusable even when the selector value looks valid.

## Important APIs, Types, and Functions

The test creates a busy-loop pthread in `threadproc()` to encourage repeated kernel exits on the same CPU. On x86-64 it uses `call32_from_64()` from `thunks.S`, a low 32-bit `MAP_32BIT` stack, and a small 32-bit `test_ss` function that pushes and pops through `%ss`-dependent state. `main()` pins to CPU 0 when possible, calls `usleep(2)` in a loop, and then executes the 32-bit validation thunk.

## Control Flow and State

The busy worker never terminates during the test; it only creates scheduler pressure. The main thread loops 1000 times, sleeping through syscall return paths and then validating that a compat-mode stack operation survives. State is minimal: the worker thread, optional 32-bit stack mapping, CPU affinity, and process register/segment state.

## Dependencies and Integration Points

It depends on pthreads, CPU affinity support, syscall return behavior, 64-bit builds linking `thunks.S`, fixed Linux user selectors in the thunk, and compatibility-mode execution. It complements `sigreturn.c` and `sysret_rip.c` by checking hidden segment attributes rather than IP validity.

## Risks and Test Signals

Risks include invalid cached SS attributes after SYSRET, container CPU-affinity restrictions, wrong mixed-bitness thunk setup, and failures that manifest as crashes rather than explicit comparisons. Passing output is `[OK] We survived` after 1000 syscall/sleep and compat-stack validation iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sysret_ss_attrs.c -->
