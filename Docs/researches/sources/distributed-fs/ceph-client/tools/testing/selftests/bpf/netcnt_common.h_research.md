# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netcnt_common.h

Purpose: shared layout definitions for network counter selftests using BPF local storage and per-CPU values. It provides conservative value-size constants and unions that can be used as either typed counters or raw padding buffers.

Important APIs/types/functions: defines `MAX_PERCPU_PACKETS`, `SIZEOF_BPF_LOCAL_STORAGE_ELEM`, estimated `BPF_LOCAL_STORAGE_MAX_VALUE_SIZE`, and `PCPU_MIN_UNIT_SIZE`. `union percpu_net_cnt` contains packet/byte counters plus previous timestamp and previous packet/byte snapshots, padded to `PCPU_MIN_UNIT_SIZE`. `union net_cnt` contains packet/byte counters padded to the estimated maximum local storage value size.

Control flow: header only; no executable control flow.

State and persistence behavior: no runtime state is owned here. The unions define map value memory layout used by BPF programs/userspace tests elsewhere. Padding intentionally stresses allocator and maximum value size behavior.

Dependencies and integration points: includes `linux/types.h` and is included by net counter tests and BPF programs that need consistent value layout between kernel and userspace.

Risks: `BPF_LOCAL_STORAGE_MAX_VALUE_SIZE` is an estimate derived from assumed local storage element overhead. Architecture or kernel layout changes can make the estimate conservative or stale. Large padded unions can materially affect memory use in tests.

Test signals: indirect only; consumers can verify counter values, allocation behavior, and maximum value handling when using these layouts.
