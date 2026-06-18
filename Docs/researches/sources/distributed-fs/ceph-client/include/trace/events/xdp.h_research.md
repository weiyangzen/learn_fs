# sources/distributed-fs/ceph-client/include/trace/events/xdp.h

Purpose: Defines XDP tracepoints for exceptions, bulk TX, redirects, cpumap/devmap paths, memory provider connect/disconnect, and failed BPF XDP link attachment.

Important APIs/types/functions: Provides action/memory-type symbol maps, `xdp_exception`, `xdp_bulk_tx`, redirect template events (`xdp_redirect`, `xdp_redirect_err`, map variants), helper macros `_trace_xdp_redirect*`, `xdp_cpumap_kthread`, `xdp_cpumap_enqueue`, `xdp_devmap_xmit`, `mem_disconnect`, `mem_connect`, and `bpf_xdp_link_attach_failed`.

Control flow: XDP and BPF map code emits events when programs return exceptional actions, redirect frames, enqueue/dequeue batches, transmit via devmap/cpumap, attach links, or manage page-pool memory providers. Events snapshot netdevice identity, program/map ids, action/error codes, batch counts, and memory ids.

State/persistence: XDP data path state is not owned. Trace buffers persist packet-path decisions and resource lifecycle observations.

Dependencies/integration: Includes netdevice, filter/BPF, `net/xdp.h`, and private XDP memory helpers; some events require `CONFIG_BPF_SYSCALL`.

Risks: XDP is a very hot path. Tracepoints must remain disabled-fast, avoid costly formatting unless enabled, and keep action/memory enum maps synchronized.

Test signals: Run XDP redirect, devmap/cpumap, and attach-failure selftests with `xdp:*` enabled; verify action/error/map metadata.
