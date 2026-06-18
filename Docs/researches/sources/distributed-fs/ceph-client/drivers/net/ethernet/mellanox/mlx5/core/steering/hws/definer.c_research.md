# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.c

## Purpose
`definer.c` converts mlx5 flow match masks into HWS match definer layouts and tag-generation field-copy programs. It understands outer/inner headers, misc parameter blocks, tunnels, flex parsers, registers, MPLS, GTP/Geneve/VXLAN/GRE, packet type fields, and source-port GVMI translation. It also caches firmware definer objects by selector/mask layout.

## Important APIs, Types, And Functions
Public APIs include `mlx5hws_definer_fname_to_str()`, `mlx5hws_definer_create_tag()`, `mlx5hws_definer_get_id()`, `mlx5hws_definer_compare()`, `mlx5hws_definer_calc_layout()`, cache init/uninit, `mlx5hws_definer_get_obj()`, `mlx5hws_definer_free()`, `mlx5hws_definer_mt_init()`, and `mlx5hws_definer_mt_uninit()`. Internal conversion helpers map each match criteria block into `struct mlx5hws_definer_fc` entries, assign tag setters, validate incompatible flags, build a header-layout bitmap, choose selectors recursively, bind field-copy offsets to tag offsets, create tag masks, and allocate/cache firmware definers.

## Control Flow And State
Match-template initialization allocates a full field-copy array, converts enabled criteria blocks into header-layout offsets, validates conflicts, compresses active field copies into `mt->fc`, and fills an `hl` mask. `hws_definer_find_best_match_fit()` first tries normal match selectors; if that fails and jumbo is allowed, it tries jumbo/full-limited selector layouts based on firmware caps. `hws_definer_fc_bind()` maps header-layout byte offsets into final tag offsets selected by the definer. A definer object is then looked up in `ctx->definer_cache`; matching selector and mask layouts are refcounted and moved to the front of the list, otherwise `mlx5hws_cmd_definer_create()` creates a new object.

Tag generation later iterates `mt->fc` and calls each field’s setter to copy or synthesize bits into the hardware tag. Some setters synthesize values, such as VLAN type, L3 type, ICMP words, parser OK bits, or GVMI from source port and peer context.

## Dependencies And Integration Points
This file depends heavily on mlx5 PRM field macros, firmware capabilities, vport GVMI lookup, peer context xarray, command definer create/destroy, match template lifetime, BWC complex detection, and debug dumping of selectors/masks. `bwc_complex.c` also calls `mlx5hws_definer_calc_layout()` with jumbo disabled to determine when masks must be split.

## Risks And Test Signals
Risks include incorrect bit/byte offsets, endian errors in tag setters, unsupported misc blocks returning the wrong error, selector search exponential behavior, conflicts among tunnel/protocol flags, stale definer-cache refcounts, source-port GVMI lookup under wrong peer context, and jumbo-vs-complex decisions that change rule semantics. Test signals include exact tag vectors for every field family, unsupported-field negative cases, jumbo and non-jumbo layout boundaries, complex-split `-E2BIG` behavior, cache reuse/free refcounts, tunnel parser capability matrices, IPv4/IPv6 and VLAN synthesis, and peer-vport source matching.
