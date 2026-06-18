# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/varlen.c

## Purpose

Selftest for variable-length reads and copied payload accounting in `test_varlen` BPF programs. It verifies that split input strings are captured into BSS/data buffers with correct lengths and that a deliberately bad read reports `-EFAULT` without corrupting sentinel bytes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_varlen__open_and_load()`, `test_varlen__attach()`, skeleton BSS/data sections, `memcpy()`, `memcmp()`, `usleep()`, and `CHECK_VAL`/`CHECK` assertions.

## Control Flow

The test loads and attaches the skeleton, sets `test_pid`, writes `Hello, ` and `World!` into BSS input buffers, toggles `capture`, sleeps briefly to let attached programs run, then checks four copied payload variants and bad-read sentinel state.

## State and Persistence Behavior

All state is skeleton memory: BSS inputs/control flags and BSS/data output payloads. It is destroyed with the skeleton and has no persistence beyond the test process.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Timing is minimal (`usleep(1)`), so failures can expose attach/trigger timing or scheduler assumptions. Payload expectations include embedded NUL bytes, making length-aware comparisons required.

## Test Signals

Passing signals are exact length totals, exact concatenated payload bytes with embedded NULs, `ret_bad_read == -EFAULT`, and unchanged sentinel bytes around the bad read output.
