# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_loop.c

## Purpose
This selftest validates behavior of the `bpf_loop` helper through a generated skeleton that exposes multiple BPF programs. It checks normal loop counts, early callback stop, null callback context, invalid flags, nested loops, nonconstant callback selection, and stack/map behavior across loop callbacks.

## Important APIs, Types, And Functions
Important functions are `check_nr_loops()`, `check_callback_fn_stop()`, `check_null_callback_ctx()`, `check_invalid_flags()`, `check_nested_calls()`, `check_non_constant_callback()`, `check_stack()`, and `test_bpf_loop()`. The userspace side uses `bpf_program__attach()`, skeleton BSS/data fields, `bpf_map_update_elem()`, and `bpf_map_lookup_elem()`.

## Control Flow
`test_bpf_loop()` opens and loads `bpf_loop`, sets the test PID in BSS, and runs each subtest. Each subtest attaches one BPF program, mutates control fields in BSS/data, sleeps briefly so the attached program can run, then checks output fields or map values. The stack test prepopulates a map, runs the BPF program, and confirms every value was incremented.

## State And Persistence Behavior
State is kept in the skeleton's BSS/data and one BPF map. Attachments are temporary links destroyed after each check. There is no persistent filesystem state. Because the program execution is asynchronous relative to userspace writes, the test uses small sleeps to allow attached programs to observe BSS changes.

## Dependencies And Integration Points
It depends on the `bpf_loop` BPF program skeleton, the selftest harness, and whatever attach point the skeleton programs use. It integrates helper return semantics with userspace-visible BSS counters and a BPF map used for stack callback verification.

## Risks And Edge Cases
Timing is the main risk: the test assumes `usleep(1)` is enough for the attached BPF program to execute and update BSS state. It also checks exact errno values for too many loops and invalid flags, so kernel helper contract changes would be visible.

## Test Signals
Passing signals include exact returned loop counts for zero and 500 loops, `-E2BIG` for excessive loop count, early stop at `stop_index + 1`, `-EINVAL` for flags, correct nested-loop multiplication, correct selected callback output, and map values incremented by one.
