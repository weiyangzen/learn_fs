# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/type_cast.c

## Purpose
Tests BPF type casting helpers/kfuncs against XDP metadata and skb contexts, plus negative verifier cases for invalid casts.

## APIs, Types, and Functions
Entry point `test_type_cast()` runs `test_xdp()`, `test_tc()`, and `test_negative()`. It uses `type_cast.skel.h`, `bpf_prog_test_run_opts`, and packet data from `network_helpers`.

## Control Flow, State, and Persistence
Each positive subtest opens the skeleton with only the relevant program autoloaded, loads it, runs with `pkt_v4`, checks retval, and validates BSS fields such as ifindex, ingress ifindex, netdev name, inode, skb lengths, metadata length, and fragment length. Negative tests open the skeleton, autoload one named invalid program, and require load failure.

## Dependencies and Integration
Depends on XDP and TC program test-run support, BTF-aware type casts in BPF code, loopback interface assumptions, and the generated skeleton.

## Risks and Test Signals
Risks include interface index/name assumptions, verifier diagnostic changes hidden by generic failure assertions, and packet context differences. Signals are exact BSS values for positive casts and load failure for `untrusted_ptr` and `kctx_u64`.
