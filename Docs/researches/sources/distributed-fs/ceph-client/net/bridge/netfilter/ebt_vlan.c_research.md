# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_vlan.c

## Purpose
Implements the legacy ebtables `vlan` match for 802.1Q VLAN ID, priority, and encapsulated protocol fields.

## Important APIs, Types, And Functions
Core code includes `ebt_vlan_mt`, `ebt_vlan_mt_check`, `xt_match ebt_vlan_mt_reg`, and macros `GET_BITMASK` / `EXIT_ON_MISMATCH`, using `struct ebt_vlan_info`.

## Control Flow
Runtime reads either the skb accelerated VLAN tag or an inline `struct vlan_hdr`, extracts TCI, VLAN ID, priority, and encapsulated protocol, then applies requested comparisons with inversion. Validation requires outer ethproto 802.1Q, validates bitmask/inversion masks, handles VID 0 priority-tag rules, drops priority matching when a nonzero VID is requested, validates priority range, and rejects encapsulated length values below Ethernet minimum.

## State And Persistence Behavior
No mutable state exists. Match criteria are per-rule constants.

## Dependencies And Integration Points
Depends on VLAN header helpers, accelerated VLAN tag metadata, ebtables UAPI, xtables registration, and bridge ethproto matching in ebtables core.

## Risks And Test Signals
Risks include differing behavior between hardware-accelerated and inline tags, VID 0 priority semantics, and encapsulated proto/length validation. Tests should cover accelerated tags, inline VLAN headers, VID, priority, encapsulated protocol, inversions, invalid masks, priority with nonzero VID, and short frames.
