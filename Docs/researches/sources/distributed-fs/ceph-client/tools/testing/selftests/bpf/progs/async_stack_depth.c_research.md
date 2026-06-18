# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/async_stack_depth.c

## Purpose

Negative verifier tests for combined stack depth across normal pseudo-calls and asynchronous timer callbacks. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_HASH` holding `struct bpf_timer`, `bpf_timer_set_callback()`, noinline `timer_cb()`/`bad_timer_cb()`, TC sections annotated `__failure` and `__msg("combined stack size of 2 calls is")`.

## Control Flow

Both TC programs allocate a 256-byte stack buffer and look up a timer element. One calls a 256-byte callback directly and sets it as timer callback; the other sets a callback that uses 300 bytes and calls the first callback. Both are expected to fail verifier combined-stack checks.

## State and Persistence Behavior

Only the hash map/timer value and stack buffers are involved; programs should not load successfully.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on verifier support for async callback stack accounting and selftest expected-failure annotations.

## Risks and Edge Cases

Verifier diagnostic text is part of the contract. Stack-size calculations can shift if callback accounting changes.

## Test Signals

Expected verifier rejection with message containing `combined stack size of 2 calls is` for both programs.
