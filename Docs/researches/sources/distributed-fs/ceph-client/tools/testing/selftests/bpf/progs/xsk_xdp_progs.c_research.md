<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c

## Purpose
This AF_XDP test program collection redirects packets to XSKMAP sockets and exercises drop behavior, custom metadata population, shared UMEM routing, and XDP tail adjustment.

## Important APIs, Types, and Functions
It declares XSKMAP `xsk`, static/global counters `idx`, `adjust_value`, and `count`, and uses `bpf_redirect_map`, `bpf_xdp_adjust_meta`, `bpf_xdp_get_buff_len`, `bpf_xdp_adjust_tail`, and `bpf_xdp_store_bytes`. Metadata layout comes from `xsk_xdp_common.h`.

## Control Flow
`xsk_def_prog` redirects all packets to socket 0. `xsk_xdp_drop` drops every other packet using a static counter. `xsk_xdp_populate_metadata` reserves metadata, validates it, writes incrementing `count`, and redirects. `xsk_xdp_shared_umem` parses Ethernet, chooses socket index from the last destination MAC byte divided by two, validates it, and redirects. `xsk_xdp_adjust_tail` records current length, adjusts tail by `adjust_value`, handles `-EOPNOTSUPP` specially by writing it back to the global, validates new length, optionally writes a sequence number near the new packet end, and redirects.

## State and Persistence
Persistent state includes XSKMAP bindings, global `adjust_value`, static drop index, selected `idx`, and `count`. Packet metadata and tail bytes are modified in specific programs.

## Dependencies and Integration Points
It integrates with AF_XDP/xsk selftests and shared UMEM tests. It depends on XDP frags support for most entry points and shared definitions such as `MAX_SOCKETS` and `PKT_HDR_ALIGN`.

## Risks
Socket index bounds depend on `MAX_SOCKETS`; if the computed index equals the map max it may rely on helper fallback action. Tail adjustment support varies by driver and frame mode, hence the explicit `-EOPNOTSUPP` path.

## Test Signals
Userspace observes redirect/drop cadence, metadata counts, selected socket routing by destination MAC, `adjust_value` updates on unsupported tail adjustment, and final packet length/sequence marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xsk_xdp_progs.c -->
