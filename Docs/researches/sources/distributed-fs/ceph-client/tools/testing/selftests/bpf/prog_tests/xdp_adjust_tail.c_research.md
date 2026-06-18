# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_tail.c

## Purpose

XDP tail adjustment regression suite for shrinking and growing linear and fragmented packets, including page-size-specific behavior and data zeroing/untouched-region checks. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_prog_test_run_opts()`, `bpf_object__open/load`, `getpagesize()`, XDP return codes, packet fixtures, and BPF objects `test_xdp_adjust_tail_shrink.bpf.o`/`test_xdp_adjust_tail_grow.bpf.o`.

## Control Flow

Subtests load shrink/grow programs, run IPv4/IPv6 fixture cases, validate `data_size_out`, then run synthetic packet-size cases for maximum grow and ENOSPC copy limits. Fragment subtests allocate 9KB/16KB/256KB buffers and check shrinking pages, growing last fragments, zero-filled new bytes, untouched tail bytes, and too-large grow drops. `test_xdp_adjust_tail()` dispatches page-size-specific variants.

## State and Persistence Behavior

State is only heap buffers, stack buffers, and loaded BPF objects. Page size influences expected paths but is not changed.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP test-run packet allocator layout, `skb_shared_info` tailroom assumptions, and architecture cacheline/page details.

## Risks and Edge Cases

Expected max grow/tailroom is architecture-sensitive; 64K page systems use different paths. Buffer aliasing via `data_in == data_out` makes size reset between calls important.

## Test Signals

Expected `XDP_DROP`/`XDP_TX`, exact output sizes such as IPv6 shrink/grow, ENOSPC with reported output size, zero-filled grown regions, and drop on too-large multi-buffer grow.
