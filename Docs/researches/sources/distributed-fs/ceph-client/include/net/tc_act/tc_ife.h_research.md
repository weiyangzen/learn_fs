<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h

Purpose: Defines TC IFE action state and metadata operation registration for Inter-FE encapsulation metadata.

Important APIs/types/functions: `struct tcf_ife_params` stores destination/source MAC, ethertype, flags, metadata list, and RCU head. `struct tcf_ife_info` embeds `tc_action` and RCU params. `struct tcf_meta_info` binds a metadata operation to a value and id. `struct tcf_meta_ops` defines check, encode, decode, get, alloc, release, and validate callbacks plus module ownership. Helpers allocate, check, encode, validate, and release u16/u32 metadata; `register_ife_op()` and `unregister_ife_op()` manage metadata plugins.

Control flow: IFE action setup builds a metadata list and Ethernet encapsulation parameters. Packet execution encodes or decodes metadata through registered `tcf_meta_ops`. Metadata modules register their ids and callbacks before use.

State and persistence behavior: Action params are RCU-replaced; metadata op registry is global module state; metadata values live in per-action lists.

Dependencies/integration points: Depends on `act_api.h`, Ethernet helpers, RTNL, and module aliases `ife-meta-*`. Integrated with `tcf_ife_act`.

Risks: Metadata module lifetime and list ownership must be correct. Encode/decode length validation is security-sensitive.

Test signals: IFE encode/decode round trips for u16/u32 metadata, module register/unregister, malformed metadata length rejection, action replacement, and MAC/ethertype dump tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ife.h -->
