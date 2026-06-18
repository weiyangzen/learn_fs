
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iter_buf_null_fail.c

## Purpose

`iter_buf_null_fail.c` is a verifier negative-test wrapper for iterator buffer NULL handling.

## Important APIs, Types, and Functions

The file includes `iter_buf_null_fail.skel.h` and invokes `RUN_TESTS(iter_buf_null_fail)`, which runs all annotated skeleton verifier cases through the selftest framework.

## Control Flow and Data Flow

There is no custom control flow beyond delegating to `RUN_TESTS`. The paired BPF object contains the individual programs and expected outcomes.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier load result and framework subtest metadata. Dependencies are the generated skeleton and verifier expectations embedded in the BPF source. Integration is iterator buffer pointer validation. Risks are opaque coverage from the C wrapper alone and verifier log wording drift in the paired object. Test signal is `RUN_TESTS` passing all negative cases.
