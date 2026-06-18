# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/pedit.c

Purpose: Parses TC pedit mangle/add actions into mlx5 modify-header software shadow structures.

Important APIs: `mlx5e_tc_act_pedit_parse_action()` is shared by VLAN rewrite code. `mlx5e_tc_act_pedit` parses action entries, sets MOD_HDR, and for FDB updates split/output parse state.

Control flow: The parser rejects legacy unspecified pedit and namespaces without mod-hdr support. It maps header type to offsets inside `struct pedit_headers`, inverts the TC mask, and records masked values in set/add slots. Acting twice on the same masked location is rejected.

State and dependencies: Mutates `attr->parse_attr->hdrs[cmd]`, `attr->action`, `esw_attr->split_count`, and `parse_state->if_count`. Depends on `en/mod_hdr.h`, TC pedit constants, and namespace helpers.

Risks and tests: Offset and mask handling is sensitive to endianness and header layout. Tests should cover SET and ADD, duplicate location rejection, unsupported legacy pedit, namespace without mod-hdr actions, FDB split reset, and each supported header type.
