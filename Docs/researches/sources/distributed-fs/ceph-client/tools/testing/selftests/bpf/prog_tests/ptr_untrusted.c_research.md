# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ptr_untrusted.c

## Purpose
Verifies verifier and attach behavior for programs that handle untrusted pointers across LSM and raw tracepoint contexts. The source was read as a complete 37-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `serial_test_ptr_untrusted()`.
- Includes and fixtures: `#include <string.h>`, `#include <linux/bpf.h>`, `#include <test_progs.h>`, `#include "test_ptr_untrusted.skel.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `test_ptr_untrusted`.
- Primary APIs and types: `test_ptr_untrusted__open()`, `bpf_program__attach_lsm()`, `bpf_program__attach_raw_tracepoint()`, program name comparison, and skeleton load.

## Control Flow
The serial test opens/loads the skeleton, attaches the LSM program, attaches a raw tracepoint program, and compares tracepoint naming/metadata expected by the test.

## State and Persistence Behavior
Only link lifetimes are persistent during the test. No maps or bpffs entries persist.

## Dependencies and Integration Points
Depends on `test_ptr_untrusted.skel.h`, LSM BPF support, raw tracepoint support, and serial execution for attach side effects.

## Risks and Edge Cases
Kernels without BPF LSM enabled will skip/fail; raw tracepoint names must match kernel tracepoint availability.

## Test Signals
Assertions check skeleton open, LSM attach, raw tracepoint attach, and tracepoint name comparison. Named assertion/check labels observed in the source include: `skel_open`, `lsm_attach`, `raw_tp_attach`, `cmp_tp_name`.
