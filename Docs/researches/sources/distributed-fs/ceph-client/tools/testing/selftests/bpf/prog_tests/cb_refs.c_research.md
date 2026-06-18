# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cb_refs.c

## Purpose
This verifier-negative test validates reference tracking across callback-style BPF programs. It ensures selected programs fail to load with specific verifier diagnostics for invalid callback reference transfer, leaks, underflow, or nested-callback reference ownership.

## APIs, Types, and Functions
It uses `cb_refs.skel.h`, `bpf_object_open_opts` with a large kernel verifier log buffer, `bpf_object__find_program_by_name`, `bpf_program__set_autoload`, skeleton load/destroy helpers, and `bpf_prog_test_run_opts` with `pkt_v4` input from network helpers.

## Control Flow
For each entry in `cb_refs_tests`, the test opens the skeleton with verifier logging, autoloads only the named program, expects skeleton load to fail, optionally runs the program if load unexpectedly succeeds, and checks that the verifier log contains the expected diagnostic substring.

## State, Dependencies, and Integration
State is the global verifier log buffer and transient skeleton object. It integrates directly with kernel verifier diagnostics, so it depends on exact or near-exact verifier wording.

## Risks and Test Signals
The test signal is expected load failure plus diagnostic substring match. It is intentionally brittle to verifier message changes but valuable for catching reference-tracking regressions.
