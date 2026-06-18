# sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_kern.c

Purpose: minimal BPF kprobe/kretprobe object used to demonstrate querying BPF program attachment information through task file descriptors.

Important APIs/types/functions: `SEC("kprobe/blk_mq_start_request") int bpf_prog1` and `SEC("kretprobe/__blk_account_io_done") int bpf_prog2`.

Control flow: both probe handlers return immediately; their purpose is attachment presence rather than data collection.

State and persistence: no maps or persistent BPF state beyond loaded programs and links/events.

Dependencies and integration: paired with `task_fd_query_user.c` in the broader sample suite; depends on block-layer symbols existing for kprobe attachment.

Risks: target symbols may be absent or renamed on some kernels/configs. Because handlers are no-ops, correctness is in attach/query behavior rather than runtime effects.

Test signals: user query sample can attach these probes and retrieve expected task FD query metadata.
