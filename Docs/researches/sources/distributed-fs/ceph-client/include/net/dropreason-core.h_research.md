# sources/distributed-fs/ceph-client/include/net/dropreason-core.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason-core.h` completely for this pass (637 lines, 20902 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason-core.h_research.md`.

Purpose: defines the core `enum skb_drop_reason` namespace and helper macros used to annotate packet drops throughout the network stack for tracing, diagnostics, and reason-aware freeing.

Important APIs/types/functions: `DEFINE_DROP_REASON(FN, FNe)` is the master macro list for core reasons. `enum skb_drop_reason` starts with `SKB_NOT_DROPPED_YET` and `SKB_CONSUMED`, then expands detailed core reasons covering sockets, TCP, UDP, IP, XFRM, BPF, neighbor, qdisc, backlog, XDP/TC, skb/GSO/copy errors, device readiness/ring fullness, ICMP/IP validation, fragmentation, IPv6 NDISC/extension headers, TC cookie/chain/reclassify, VXLAN/tunnel, bridge, CAN, PFMEMALLOC, PSP, and recursion limit. `SKB_DROP_REASON_SUBSYS_MASK` reserves high bits for subsystem-specific reasons. Macros `SKB_DR_INIT`, `SKB_DR`, `SKB_DR_SET`, and `SKB_DR_OR` simplify local reason variables.

Control flow: packet-processing code initializes a reason variable, updates it when a specific failure is discovered, and passes the reason to drop/free paths. `SKB_DR_OR()` preserves the first specific reason unless the current value is unspecified or not-dropped. Tracing code uses the enum values and generated reason strings to expose drop diagnostics.

State and persistence: no runtime state is stored. The enum values are ABI/trace-facing identifiers and must remain stable enough for tooling. Local reason variables live only within packet-processing paths.

Dependencies and integration points: included by `dropreason.h`, qdisc drop reasons, kfree skb tracing, protocol receive/transmit paths, TC/XDP/netfilter/tunnel/bridge/CAN/PSP code, and monitoring tools consuming drop reason strings.

Risks: inserting/renumbering reasons can affect trace consumers. `SKB_DROP_REASON_MAX` is not a real drop reason. Reason selection must avoid overwriting more specific earlier failures. Core reasons overlap broad domains; using a generic reason where a specific reason exists reduces observability.

Test signals: compile-time generation of reason strings, tracepoint output for representative TCP/IP/qdisc/XDP/netfilter/tunnel drops, first-reason preservation with `SKB_DR_OR()`, subsystem mask handling, and userspace tooling compatibility with enum/string updates.
