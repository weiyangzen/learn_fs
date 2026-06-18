
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_func_args.c

## Purpose

`global_func_args.c` validates passing and mutating arguments through global BPF functions, including NULL pointers, return values, local/global variables, and pointer-to-pointer writes.

## Important APIs, Types, and Functions

The file loads `test_global_func_args.bpf.o` as `BPF_PROG_TYPE_CGROUP_SKB`, runs it with `bpf_prog_test_run_opts()`, finds the `values` map with `bpf_find_map()`, and looks up indexed expected results.

## Control Flow and Data Flow

The BPF program is run once against `pkt_v4`; afterward `test_global_func_args0()` iterates seven expected result slots and compares map values with the expected semantics for each global function argument case.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the `values` map populated by the BPF object. Dependencies include global subprogram support, cgroup skb test-run, and packet fixture availability. Integration is verifier and codegen support for global function argument passing. Risks are paired BPF object result-index drift. Test signals are successful load/run and exact values `[0, 1, 100, 101, 42, 43, 1]`.
