# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/vmlinux/vmlinux.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/vmlinux/vmlinux.h

Purpose: this hand-maintained minimal `vmlinux.h` supplies non-UAPI kernel types and fields needed by perf's BPF skeletons when building without a generated full vmlinux header.

Important definitions: it defines fixed-width aliases, `timespec64`, cgroup subsystem id, softirq enum, atomic/spinlock/mutex/rwsem/task/cgroup/css structs, tracepoint raw structs for IRQ/softirq/workqueue, `perf_sample_data`, `perf_event`, `bpf_perf_event_data_kern`, `rq`, `kmem_cache`, `bpf_iter__kmem_cache`, `zone`, and `pglist_data`. Most structs use `preserve_access_index` for CO-RE relocation.

Control flow and state: no executable logic. The header is a build-time type contract for BPF C files.

Dependencies and integration: included by nearly all files under `bpf_skel`. It must provide just enough fields for BPF programs while allowing libbpf CO-RE relocation against real kernel BTF.

Risks: missing fields break compilation; incorrect approximations can break CO-RE relocation or verifier behavior. The fake `perf_event_cgrp_id = 8` is relocated when enum preservation is available but remains a fallback otherwise. `pglist_data.node_zones[6]` is a placeholder and user space supplies actual zone size for lock contention.

Test signals: build all skeletons with and without generated vmlinux support; load on kernels with varied struct layouts; and run skeleton-specific CO-RE tests.
