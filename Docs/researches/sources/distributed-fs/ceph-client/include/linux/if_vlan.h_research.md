# `sources/distributed-fs/ceph-client/include/linux/if_vlan.h`

Purpose: internal VLAN 802.1Q/802.1ad API for header layouts, SKB tag manipulation, device-private VLAN state, hardware acceleration metadata, protocol extraction, feature filtering, and VLAN device management hooks.

Important APIs/types/functions: `struct vlan_hdr`, `struct vlan_ethhdr`, tag masks (`VLAN_PRIO_MASK`, `VLAN_CFI_MASK`, `VLAN_VID_MASK`), `struct vlan_pcpu_stats`, `struct vlan_priority_tci_mapping`, `struct vlan_dev_priv`, VLAN device lookup/metadata functions, `is_vlan_dev`, `vlan_dev_get_egress_qos_mask`, `eth_type_vlan`, tag insertion/removal helpers, hwaccel tag helpers, `vlan_get_tag`, `vlan_get_protocol*`, `skb_protocol`, `skb_vlan_tagged`, `skb_vlan_tagged_multi`, `vlan_features_check`, and `compare_vlan_header`.

Control flow and state: persistent VLAN state is in `vlan_dev_priv` with ingress/egress priority maps, proto/id/flags, lower-device reference, proc entry, per-CPU stats, and optional netpoll. Inline data path code may grow SKB headroom, move MAC header bytes, manipulate `skb->vlan_all/vlan_tci/vlan_proto`, parse nested VLANs up to bounded depth through implementation functions, and mask off unsafe offload features for multi-tagged packets.

Dependencies/integration: depends on netdevice, skbuff, rtnetlink, Ethernet helpers, UAPI VLAN definitions, notifiers, RCU, and `CONFIG_VLAN_8021Q`. It is used by core RX/TX, drivers, offload, bridges, and virtual network devices.

Risks: SKB headroom failures transfer ownership for wrapper helpers that free on error; direct `__vlan_insert_*` helpers do not free; hardware-accelerated vs in-payload tags must be kept consistent; egress QoS map traversal requires RCU; protocol extraction can fail if headers are not pulled; disabled-config stubs can hide missing VLAN support; multi-tag feature masking is security/correctness-sensitive.

Test signals: single and stacked VLAN RX/TX, C-tag and S-tag offload, SKB headroom exhaustion, vlan tag get/remove/insert ownership behavior, egress QoS mapping under RCU, protocol extraction with short/nonlinear SKBs, feature masking for QinQ, and builds with VLAN disabled.
