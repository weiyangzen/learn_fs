# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_test_run.c

## Purpose
Tests writable raw tracepoint program execution through test-run APIs using an NBD request-like context. The source was read as a complete 84-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `serial_test_raw_tp_writable_test_run()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <linux/nbd.h>`, `#include "bpf_util.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_load()` helpers from `bpf_util.h`, `bpf_prog_test_run_opts()`, `linux/nbd.h` structures, and raw tracepoint writable program type/attach type.

## Control Flow
The serial test loads a writable raw tracepoint program, prepares an NBD-style context, runs it via test-run, and verifies that permitted writable fields are modified while invalid fields remain protected.

## State and Persistence Behavior
State is entirely local: context buffer before/after, run options, and program fd. No link or bpffs state persists.

## Dependencies and Integration Points
Depends on writable raw tracepoint test-run support and NBD tracepoint layout headers.

## Risks and Edge Cases
Tightly coupled to NBD tracepoint ABI and verifier writable-field policy; kernel config can remove the relevant tracepoint types.

## Test Signals
Signals are successful load/test-run and expected context mutation or rejection results. Named assertion/check labels observed in the source include: `failed: %d errno %d\n`, `tracepoint did not modify return value\n`, `socket_filter did not return 0\n`, `test_run failed with %d errno %d\n`.
