# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/time_tai.c

## Purpose
Validates BPF access to TAI time by comparing timestamps produced by `test_time_tai` BPF code against user-space `CLOCK_TAI`.

## APIs, Types, and Functions
The file exposes `test_time_tai()`. `ts_to_ns()` converts `timespec` to nanoseconds. It uses `bpf_prog_test_run_opts` with an IPv4 packet and `__sk_buff` context, where the BPF program writes two TAI values into `skb.tstamp` and `skb.cb`.

## Control Flow, State, and Persistence
The skeleton is opened and loaded, the TC/XDP-style test program is run once, and two timestamps are recovered from the output context. Assertions verify nonzero values, monotonic ordering, timestamps not in the future, and a one-second freshness threshold. State is transient in stack variables and the generated skeleton.

## Dependencies and Integration
Depends on `test_progs.h`, `network_helpers.h`, `test_time_tai.skel.h`, `clock_gettime(CLOCK_TAI)`, and `bpf_prog_test_run_opts`.

## Risks and Test Signals
Risks include systems without correct TAI clock support, scheduling delays exceeding the threshold, and context-output layout mismatches. Passing signals are successful skeleton load, program test-run success, nonzero ordered timestamps, and less-than-one-second delta to user-space TAI.
