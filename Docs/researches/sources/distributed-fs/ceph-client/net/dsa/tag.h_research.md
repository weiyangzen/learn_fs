# sources/distributed-fs/ceph-client/net/dsa/tag.h

## Purpose
This private header defines DSA tag driver metadata, tagger registration macros, RX/TX helper functions for taggers, VLAN software untagging helpers, and module alias conventions.

## Important APIs, Types, And Functions
`struct dsa_tag_driver` binds `struct dsa_device_ops` to a list node and owner module. The header declares tagger lookup/refcount APIs and `dsa_pack_type`. Inline helpers include `dsa_tag_protocol_overhead()`, `dsa_conduit_find_user()`, `dsa_software_vlan_untag()`, bridge PVID untag helpers, `dsa_find_designated_bridge_port_by_vid()`, `dsa_default_offload_fwd_mark()`, EtherType header strip/allocate/position helpers, and `dsa_xmit_port_mask()`.

Macros define module aliases (`dsa_tag:<name>` and `dsa_tag:id-<proto>`), `DSA_TAG_DRIVER()`, `module_dsa_tag_driver()`, and `module_dsa_tag_drivers()`.

## Control Flow
Tagger modules use the macros to create static driver objects and module init/exit functions that register/unregister them with `tag.c`. TX helpers manipulate skb headroom for taggers that insert EtherType-like headers. RX helpers locate user netdevs, clear hardware-accelerated VLAN tags when bridge semantics require software untagging, and compute HSR duplicate port masks.

`dsa_software_vlan_untag()` first finds the ingress DSA user port's bridge, moves inline VLAN tags to hwaccel if needed, obtains the VID, and clears the tag depending on VLAN-aware or VLAN-unaware bridge settings. The VLAN-unaware helper contains an explicit FIXME: it currently assumes the private VID equals the bridge PVID.

## State And Persistence
The header stores no global state, but its helpers read DSA tree port lists, bridge membership, tagger operation fields, skb VLAN metadata, and HSR port state.

## Dependencies And Integration Points
It depends on VLAN, bridge VLAN APIs, public `<net/dsa.h>`, DSA port/user helpers, skb layout conventions, HSR feature flags, and tag driver modules.

## Risks And Edge Cases
The VLAN-unaware untagging FIXME is a known correctness risk for drivers whose private VID differs from bridge PVID. Header manipulation helpers require callers to have already pushed/pulled the expected bytes. `dsa_conduit_find_user()` matches by switch index and port; stacked or metadata-driven paths must provide the right device/port tuple. Macro-generated module init/exit allows only one use per module.

## Test Signals
Tests should cover tagger module alias generation, skb header helpers with headroom/tailroom, VLAN-aware and VLAN-unaware software untagging, designated bridge port selection by VID, HSR port mask generation, and lookup of user devices in multi-switch trees.
