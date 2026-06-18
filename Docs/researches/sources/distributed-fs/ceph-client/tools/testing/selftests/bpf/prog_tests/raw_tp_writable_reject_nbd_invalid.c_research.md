# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_reject_nbd_invalid.c

## Purpose
Verifies that invalid writable raw tracepoint programs for NBD tracepoints are rejected by the verifier. The source was read as a complete 44-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_raw_tp_writable_reject_nbd_invalid()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <linux/nbd.h>`, `#include "bpf_util.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_load()`/raw instruction loading via `bpf_util.h`, `linux/nbd.h` tracepoint context definitions, and selftest load-failure checks.

## Control Flow
The test builds or loads an intentionally invalid writable raw tracepoint program targeting NBD context and expects program load to fail.

## State and Persistence Behavior
No persistent state; failed load leaves no program/link. Any generated log is local.

## Dependencies and Integration Points
Depends on NBD tracepoint type definitions, writable raw tracepoint verifier paths, and `bpf_util.h` helpers.

## Risks and Edge Cases
Tracepoint context changes or missing NBD config can alter expected rejection; verifier message text may vary.

## Test Signals
Test passes when the invalid writable raw tracepoint load is rejected with the expected failure mode. Named assertion/check labels observed in the source include: `failed: %d errno %d\n`, `erroneously succeeded\n`.
