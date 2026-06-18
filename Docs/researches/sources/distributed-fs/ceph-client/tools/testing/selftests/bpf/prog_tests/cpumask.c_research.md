# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpumask.c

## Purpose
Validates BPF cpumask kfunc success cases and verifier failure cases.

## Important APIs, types, and functions
Uses `cpumask_success.skel.h`, `cpumask_failure.skel.h`, a table of success program names, `bpf_object__find_program_by_name()`, `bpf_program__set_autoload()`, skeleton load/attach, and BSS error checks.

## Control flow and state
For each success program, the skeleton is opened, only the named program is autoloaded, loaded/attached or test-run as defined by the skeleton, and error state is checked. Then `RUN_TESTS(cpumask_failure)` executes negative coverage. State is skeleton BSS and per-program autoload setting.

## Dependencies and integration points
Depends on kernel cpumask kfunc support, generated success/failure BPF objects, and selftest harness. Integrated through `test_cpumask()`.

## Risks and test signals
Risks include missing kfunc support and verifier semantic changes. Signals are zero BSS errors for success cases and expected verifier failure for negative programs.
