# sources/distributed-fs/ceph-client/net/sched/act_ife.c

Purpose: implements the Inter-FE (`ife`) TC action, encoding selected packet metadata into an outer Ethernet/IFE header or decoding received IFE metadata back into skb fields.

Important APIs/functions: exported metadata helpers include `register_ife_op()`, `unregister_ife_op()`, generic u16/u32 encode/get/check/alloc/validate/release functions, and internal metadata list builders. `tcf_ife_init()` installs encode/decode params, `tcf_ife_act()` dispatches runtime encode/decode, `tcf_ife_encode()` prepends IFE metadata, `tcf_ife_decode()` parses TLVs and applies metadata ops, `tcf_ife_dump()` reports config, and `tcf_ife_cleanup()` releases metadata ops.

Control flow: metadata ops register globally by metaid/name. Init parses action params, optional destination/source MAC, ethertype, and metadata allow/use list; it autoloads missing metadata modules by known meta ID, validates values, allocates or replaces the action, validates control action, populates the metadata list or installs all registered metadata ops, and RCU-swaps params. Encode computes the total TLV size by asking each op whether metadata is present, checks MTU on egress, prepends an IFE header, encodes each TLV, and fills outer Ethernet addresses/type. Decode pushes MAC header at ingress if needed, calls `ife_decode()`, iterates TLVs, dispatches matching metadata decode ops, counts unknown metadata as overlimits, resets protocol with `eth_type_trans()`, and returns action.

State and persistence: action params contain encode/decode flag, outer Ethernet fields, ethertype, and a list of `tcf_meta_info` entries with module references and optional configured values. The global `ifeoplist` stores metadata operation providers under a rwlock. Packet metadata and headers are mutated at runtime; action state is RCU-managed.

Dependencies and integration: depends on `NET_IFE`, TC action API, IFE TLV helpers, Ethernet header helpers, module autoload aliases `ife-meta-*`, and metadata provider modules for skb mark, priority, and tcindex.

Risks: metadata op registration exports appear swapped in this source (`register_ife_op` near `EXPORT_SYMBOL_GPL(unregister_ife_op)` and vice versa), which is a review-sensitive signal. Encoding must not exceed MTU on egress and must balance ingress header push/pull. Metadata list lookup is linear. Unknown or malformed TLVs can drop packets or increment overlimit stats.

Test signals: encode/decode roundtrips for skb mark/prio/tcindex, metadata module autoload, configured versus allow-all metadata lists, egress MTU drop, malformed TLVs, missing metadata ops, dump output, module unregister/refcount behavior, and ingress header handling.
