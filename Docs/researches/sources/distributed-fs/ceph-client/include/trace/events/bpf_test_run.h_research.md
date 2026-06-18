# sources/distributed-fs/ceph-client/include/trace/events/bpf_test_run.h

## Purpose
`bpf_test_run.h` defines tracepoints used by BPF test execution paths, including a trigger event and a writable finish event where supported.

## Important APIs, types, and functions
Events are `bpf_trigger_tp` and `bpf_test_finish`. `bpf_test_finish` is generated through `BPF_TEST_RUN_DEFINE_EVENT()`, which expands to `DEFINE_EVENT_WRITABLE()` when available and otherwise to `DEFINE_EVENT()`.

## Control flow
Tests emit `bpf_trigger_tp` with a nonce to drive attached BPF programs. Finish tracing reads `*err` from an integer pointer and, in writable configurations, exposes a writable field size of `sizeof(int)` for BPF mutation tests.

## State and persistence behavior
No state is stored in the header. Event records snapshot the nonce or error value; writable-event behavior may allow attached programs to affect the pointed error in supported builds.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and tracepoint macro support for writable events. It integrates with BPF selftests and kernel BPF test-run infrastructure.

## Risks and test signals
Risks include pointer validity for `err`, behavior differences when `DEFINE_EVENT_WRITABLE` is not defined, and tests accidentally depending on a writable tracepoint in non-writable builds. Test signals are BPF selftests that attach to the trigger and finish events and verify nonce/error propagation.
