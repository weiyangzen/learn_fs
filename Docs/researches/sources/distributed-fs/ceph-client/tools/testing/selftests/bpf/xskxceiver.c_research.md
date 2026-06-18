# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.c

## Purpose

`xskxceiver.c` is the main AF_XDP packet xceiver selftest binary. It drives a large test matrix across SKB, native/driver, and zero-copy modes, validating packet ordering, content, socket teardown, bidirectional sockets, statistics, bpf_link persistence, unaligned mode, descriptor validation, 2K frames, jumbo/multi-buffer cases, and CI skip cases.

## Important APIs, Types, and Functions

Important globals are `opt_print_tests`, `opt_mode`, and `opt_run_test`. Key functions are `test__fail`, `__exit_with_error`, `ifobj_zc_avail`, `print_usage`, `validate_interface`, `parse_command_line`, `xsk_unload_xdp_programs`, `run_pkt_test`, `is_xdp_supported`, `print_tests`, and `main`. It uses types and helpers from `prog_tests/test_xsk.h`, `xsk_xdp_progs.skel.h`, `xsk.h`, `xskxceiver.h`, `xsk_xdp_common.h`, `network_helpers`, and kselftest.

## Control Flow

`main` initializes libbpf strict mode and two interface objects, reads cache-line and max-frag values from procfs, computes UMEM tailroom, parses two `-i` interfaces and mode/test options, lists tests if requested, determines shared-UMEM mode, probes native XDP and zero-copy support, reads/restores hardware ring size when supported, initializes RX/TX interfaces, creates default packet streams, sets the kselftest plan, and loops through selected modes and tests. Each test is initialized, run through its function pointer, reported as pass/skip/fail, and restored to default packet stream state.

## State and Persistence Behavior

The program mutates interface state, AF_XDP sockets/UMEMs, XDP programs, hardware ring settings, packet streams, and test descriptors. Cleanup deletes packet streams, destroys skeletons, deletes interface objects, and resets hardware ring size if changed.

## Dependencies and Integration Points

It depends on root/network setup supplied by shell tests, veth or physical interfaces, AF_XDP support, optional zero-copy support, procfs values, ethtool ring APIs, generated skeletons, and a large helper/test table in `prog_tests/test_xsk.h`.

## Risks and Test Signals

Risks include hardware/driver feature variance, shared-interface behavior, resource leaks across many tests, busy-poll timing, and descriptor edge cases that can fail only in certain modes. Signals are kselftest plan/result counts, per-mode test messages, zero-copy probing, repeated teardown success, restored hardware ring sizes, and final pass/fail based on `failed_tests`.
