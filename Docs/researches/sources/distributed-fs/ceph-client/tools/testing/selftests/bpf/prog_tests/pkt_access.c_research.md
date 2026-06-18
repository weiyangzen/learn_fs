# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_access.c

## Purpose
Runs packet-access BPF programs with IPv4 and IPv6 packets to verify direct packet load/store bounds and return values. The source was read as a complete 33-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pkt_access()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_test_run_opts()`, `network_helpers` packet fixtures, `test__load_program()` style helpers, and selftests run option structs.

## Control Flow
`test_pkt_access()` loads the packet access object and runs it once with IPv4 and once with IPv6 input data, checking both test-run syscall success and returned verdict.

## State and Persistence Behavior
No persistent kernel state beyond the loaded program fd; packet buffers and run options are stack/local.

## Dependencies and Integration Points
Depends on `network_helpers.h`, BPF_PROG_TEST_RUN support for packet programs, and the compiled packet access BPF object.

## Risks and Edge Cases
Packet fixture size or expected return mismatches can hide verifier changes; run options must provide correct data pointers and sizes.

## Test Signals
Assertions check no test-run error and expected retval for IPv4 and IPv6. Named assertion/check labels observed in the source include: `ipv4 test_run_opts err`, `ipv4 test_run_opts retval`, `ipv6 test_run_opts err`, `ipv6 test_run_opts retval`.
