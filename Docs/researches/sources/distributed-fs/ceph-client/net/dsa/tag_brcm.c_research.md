# sources/distributed-fs/ceph-client/net/dsa/tag_brcm.c

Purpose: implements multiple Broadcom DSA tag formats: modern 4-byte in-frame tag, legacy 6-byte tag, legacy tag with transmitted FCS, and prepended 4-byte tag. The formats target Broadcom switch families with different CPU-port parsing rules.

Important APIs/functions: shared helpers `brcm_tag_xmit_ll()` and `brcm_tag_rcv_ll()` build/parse the modern tag at configurable offsets. Legacy paths are `brcm_leg_tag_xmit()`, `brcm_leg_fcs_tag_xmit()`, and `brcm_leg_tag_rcv()`. Prepend paths wrap the shared helpers. Registered ops include `brcm_netdev_ops`, `brcm_legacy_netdev_ops`, `brcm_legacy_fcs_netdev_ops`, and `brcm_prepend_netdev_ops`, conditionally compiled by Kconfig.

Control flow: TX pads frames to hardware minimum lengths, inserts tags either after source MAC or before the frame, encodes destination port masks and queue mappings, and optionally appends a calculated FCS. RX validates opcodes/reason codes, decodes source port, strips tags with checksum updates, handles legacy VID 0 stripping, maps the user port, and marks non-link-local frames as hardware-forwarded.

State and persistence: no module-owned state. Packet metadata is transient, with queue mapping rewritten for Broadcom port queues.

Dependencies and integration: depends on Broadcom tag definitions, skb padding/checksum helpers, `dsa_xmit_port_mask()`, `dsa_strip_etype_header()`, and DSA tag driver registration. It integrates with bridge offload by setting `dsa_default_offload_fwd_mark()` for non-link-local RX.

Risks and test signals: risks include unaligned tag access, wrong minimum padding, FCS calculation mistakes, incorrect legacy VLAN stripping, and reserved reason-code handling. Tests should cover each enabled protocol variant, short packets, VLAN-tagged legacy RX, link-local traps, and queue/port mask selection.
