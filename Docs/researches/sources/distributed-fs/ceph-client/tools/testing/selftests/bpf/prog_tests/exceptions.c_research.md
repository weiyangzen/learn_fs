# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exceptions.c

## Purpose
Tests BPF exception support, including successful exception/throw/catch-style execution, verifier/load failures, extension attach behavior, and assertion helper behavior.

## Important APIs, types, and functions
Uses `exceptions.skel.h`, `exceptions_ext.skel.h`, `exceptions_fail.skel.h`, `exceptions_assert.skel.h`, large verifier log buffer, `bpf_prog_test_run_opts()`, and macros such as `RUN_SUCCESS` and `RUN_EXT` to encode expected return values, load/attach errors, and BSS side effects.

## Control flow and state
`test_exceptions()` runs failure, success, extension, and assertion subtests. Success paths run individual skeleton programs through test-run and compare retval/BSS state. Failure paths expect load rejection and inspect log/error conditions. Extension paths load base and extension skeletons with specified attach expectations. State is skeleton BSS/data, links, test-run contexts, and verifier log text.

## Dependencies and integration points
Depends on kernel BPF exception feature support, generated success/fail/extension/assert BPF objects, verifier log behavior, and prog test-run. Integrated as a feature-level selftest.

## Risks and test signals
Exception semantics are evolving and verifier logs can drift. Passing signals are expected load failures for invalid cases, exact return values for success programs, correct extension attach outcomes, and assertion behavior matching generated expectations.
