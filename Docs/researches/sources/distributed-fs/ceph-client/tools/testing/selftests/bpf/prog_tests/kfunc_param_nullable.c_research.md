
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_param_nullable.c

## Purpose

`kfunc_param_nullable.c` wraps selftests for kfunc nullable-parameter validation.

## Important APIs, Types, and Functions

The C harness includes `kfunc_param_nullable.skel.h` and delegates through `RUN_TESTS(kfunc_param_nullable)`.

## Control Flow and Data Flow

The generated selftest framework loads/runs each annotated BPF program from the paired skeleton; this wrapper adds no custom control flow.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier/runtime outcome metadata. Dependencies are kernel kfunc nullable annotations and the generated skeleton. Integration is verifier enforcement of nullable versus non-null kfunc parameter contracts. Risks are hidden in the paired BPF object and kernel-version feature availability. Test signal is all `RUN_TESTS` cases passing.
