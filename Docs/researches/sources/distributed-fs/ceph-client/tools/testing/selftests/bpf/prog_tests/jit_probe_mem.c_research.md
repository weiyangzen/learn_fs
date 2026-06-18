
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/jit_probe_mem.c

## Purpose

`jit_probe_mem.c` validates JIT handling of probe-memory style accesses in a packet-processing BPF program.

## Important APIs, Types, and Functions

The harness uses `jit_probe_mem.skel.h`, packet fixture `pkt_v4`, and `bpf_prog_test_run_opts()` against `test_jit_probe_mem`.

## Control Flow and Data Flow

It loads the skeleton, runs the BPF program once with IPv4 packet input, asserts no test-run error and zero BPF retval, then checks `skel->data->total_sum == 192`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the BPF data variable `total_sum`. Dependencies include JIT/probe memory support and packet test-run. Integration is JIT code generation for guarded memory probing. Risks are architecture-specific JIT differences and paired BPF object changes. Test signal is exact total sum 192 after a successful run.
