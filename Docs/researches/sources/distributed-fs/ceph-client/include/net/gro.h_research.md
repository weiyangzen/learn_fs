# sources/distributed-fs/ceph-client/include/net/gro.h

Purpose: declares Generic Receive Offload control metadata and helpers for aggregating compatible skbs before the stack processes them. It includes checksum validation/conversion, remote checksum handling, recursion guards, protocol dispatch declarations, network flush decisions, and normal-list batching.

Important APIs/types: `struct napi_gro_cb` overlays `skb->cb` with fragment pointers, data offsets, flush/count/proto fields, checksum state, encapsulation mark, recursion counter, list mode, and L3 offsets. `NAPI_GRO_CB()` accesses it. `call_gro_receive*()` enforce `GRO_RECURSION_LIMIT`. Header helpers manage GRO offsets and fast/slow pulls. Checksum macros validate pseudo-header checksums and mark checksum-unnecessary state. `skb_gro_remcsum_process()` and cleanup handle remote checksum adjustment. Flush helpers compare IPv4/IPv6 headers. `gro_normal_one()` batches normal skbs up to `net_hotdata.gro_normal_batch`.

Control flow and state: GRO receive callbacks advance `data_offset`, validate headers/checksums, compare candidate packets, set flush bits for incompatible packets, and eventually merge or pass normal skbs up. State is per-skb in the control block and per-NAPI in `gro_node`.

Dependencies and integration: depends on IP/IPv6, UDP, checksum, skbuff, `hotdata.h`, netdevice GRO nodes, indirect calls, and packet offloads.

Risks: skb control-block ownership, recursion, checksum conversion, and encapsulated offset handling are fragile. Tests should include nested tunnels, remote checksum offload, CHECKSUM_COMPLETE and CHECKSUM_UNNECESSARY paths, IPv4 ID flush logic, IPv6 traffic-class flush, batching threshold, and malformed TCP header lengths.
