# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr_test.c

## Purpose
Tests prctl get/set semantics for editable DEXCR aspects, including current value changes and on-exec inheritance.

## Important APIs, Types, and Functions
Important functions are `dexcr_prctl_onexec_test_child()`, `dexcr_prctl_aspect_test()`, wrapper tests for IBRTPD/SRAPD/NPHIE, and `main()`.

## Control Flow
For each supported/editable aspect the test rejects invalid set+clear combinations, sets and clears the current aspect, sets on-exec and clear-on-exec controls, combines current/onexec controls, then forks and execs itself to verify inheritance is applied only after exec.

## State and Persistence
Mutates the calling process DEXCR aspect controls and child inherited state. No files are persisted.

## Dependencies and Integration Points
Depends on `dexcr.c`, prctl DEXCR API, `/proc/self/exe` exec, fork/wait, and `test_harness()`.

## Risks and Test Signals
Risks include leaving aspect state changed for later tests and kernels with only partial aspect support. Signals include precise errno `EINVAL`, DEXCR SPR bit checks, and child success/failure.
