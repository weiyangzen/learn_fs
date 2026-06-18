# sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.h

## Purpose
Declares the kprobe selftest target function implemented in `trace_kprobe_selftest.c`.

## APIs, Control Flow, and State
The header contains a single prototype for `kprobe_trace_selftest_target(int a1, int a2, int a3, int a4, int a5, int a6)`. It has no executable control flow, no macros, and no persistent state.

## Dependencies, Integration, Risks, and Tests
The header integrates the selftest target with `trace_kprobe.c`. Risks are limited to signature drift between declaration and definition or accidental removal that breaks selftest builds. Test signals are compile coverage with kprobe startup tests enabled and successful execution of the kprobe tracing selftest.
