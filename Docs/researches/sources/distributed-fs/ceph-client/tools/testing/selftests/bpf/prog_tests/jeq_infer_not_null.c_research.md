
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jeq_infer_not_null.c

## Purpose

`jeq_infer_not_null.c` wraps verifier tests for nullability inference across equality comparisons.

## Important APIs, Types, and Functions

It includes `jeq_infer_not_null_fail.skel.h` and delegates to `RUN_TESTS(jeq_infer_not_null_fail)`.

## Control Flow and Data Flow

The C harness has no bespoke logic; the selftest framework loads/runs the paired negative verifier programs and checks expected failures.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier result metadata. Dependencies are the generated skeleton and verifier annotations in the BPF source. Integration is verifier reasoning for `JEQ`-derived non-null facts. Risks are verifier message/behavior changes not visible in the wrapper. Test signal is successful `RUN_TESTS` completion.
