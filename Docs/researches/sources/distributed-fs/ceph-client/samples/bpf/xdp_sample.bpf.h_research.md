<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h

## Purpose
`xdp_sample.bpf.h` is the BPF-side shared header for XDP samples. It declares common map types, global externs, MAC-swap helper, no-tear counter macros, and small errno/action constants used by tracepoint stats programs.

## Important APIs, Types, And Functions
It defines `array_map`, extern `rx_cnt` and `nr_cpus`, `XDP_REDIRECT_SUCCESS`, `XDP_REDIRECT_ERROR`, `swap_src_dst_mac()`, alias-safe `READ_ONCE()`/`WRITE_ONCE()`, `NO_TEAR_ADD()`, `NO_TEAR_INC()`, and `ARRAY_SIZE()`.

## Control Flow
The header has no standalone control flow. Including BPF programs use the macros and inline helpers to update shared counters and manipulate Ethernet addresses.

## State And Persistence
It declares map/global contracts but owns no runtime state. Included map declarations are backed by concrete BPF objects.

## Dependencies And Integration Points
It depends on `vmlinux.h`, BPF helper/tracing headers, `net_shared.h`, and `xdp_sample_shared.h`. It is included by XDP sample BPF programs and must match userspace map setup.

## Risks And Edge Cases
The no-tear macros are relaxed read/write increments and are suitable only where write concurrency is controlled or acceptable. Header-defined errno constants must stay aligned with kernel values. Broad includes can conflict with other BPF compilation environments.

## Test Signals
Compile coverage of all XDP samples and correct userspace interpretation of `struct datarec` counters are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample.bpf.h -->
