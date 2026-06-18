# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_adjust_frags.c

## Purpose

Selftest for XDP multi-buffer fragment updates through test-run. It checks that a BPF program can modify bytes in the linear head, in fragments, across the head/fragment boundary, and across fragment boundaries, and rejects unsupported oversized buffers. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_object__open()`, `bpf_object__load()`, `bpf_program__fd()`, `bpf_prog_test_run_opts()`, `/proc/sys/net/core/max_skb_frags`, `sysconf(_SC_PAGE_SIZE)`, and packet buffers carrying an offset marker.

## Control Flow

The test loads `test_xdp_update_frags.bpf.o`, allocates buffers of 128 bytes, 9000 bytes, and an oversized max-frags-plus-one size, writes an offset in the first word and marker bytes at target positions, runs the XDP program, and checks markers changed from `0xaa` to `0xbb` where supported or `-ENOMEM` for unsupported size.

## State and Persistence Behavior

Heap packet buffers and the loaded BPF object are transient. It reads but does not modify `/proc/sys/net/core/max_skb_frags`.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP multi-buffer test-run emulation and system page/max-frag settings.

## Risks and Edge Cases

Expected offsets assume the kernel test-run linear area and fragment layout. Non-default max-frag settings are called out in the assertion label and can affect the oversized-buffer case.

## Test Signals

Signals are `XDP_PASS`, exact marker mutation at 16/31, 5000/5015, 3510/3525, 7606/7621, and `-ENOMEM` for an unsupported buffer.
