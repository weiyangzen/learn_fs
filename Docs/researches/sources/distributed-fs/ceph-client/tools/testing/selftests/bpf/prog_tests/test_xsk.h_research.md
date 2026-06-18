# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.h

## Purpose
Defines the AF_XDP selftest contract shared by the test harness and `test_xsk.c`. It declares modes, return codes, socket/UMEM/interface/test state, packet stream representation, helper prototypes, and the test case tables.

## APIs, Types, and Functions
Important types are `enum test_mode`, `struct xsk_socket_info`, `struct xsk_umem_info`, `struct ifobject`, `struct pkt`, `struct pkt_stream`, and `struct test_spec`. Function pointer typedefs describe validation callbacks, worker thread entry points, and test case functions. Inline helpers provide integer ceiling division, procfs integer reads, packet-continuation decoding, and mode-name formatting.

## Control Flow, State, and Persistence
The header has no runtime control flow beyond inline helpers, but it defines all state that persists across individual test phases: selected XDP mode, bind flags, ring sizes, XSK map/program pointers, UMEM layout, per-socket packet streams, validation callbacks, MTU, step count, and failure flags. The `tests[]` array lists default cases and `ci_skip_tests[]` isolates flaky, hugepage-dependent, hardware-ring-dependent, long, or otherwise unsuitable cases for CI.

## Dependencies and Integration
Includes Linux ethtool and if_xdp UAPI, kselftest utilities, and local `xsk.h`. It is consumed by AF_XDP test runner code and by `test_xsk.c`; generated XDP skeleton types are forward-referenced through `struct xsk_xdp_progs`.

## Risks and Test Signals
Risks are ABI drift between declarations and implementation, duplicated constants such as packet sizes, and stale CI skip policy. Build failures catch type/prototype drift; runtime signals come from each named `testapp_*()` case being discovered and run under SKB, DRV, or ZC modes as supported.
