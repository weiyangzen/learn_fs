# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/definer.h

## Purpose
`definer.h` describes the Hardware Steering match-definer vocabulary for mlx5. It maps Linux flow-match fields into HWS definer field names, selector limits, high-level packet header layouts, match tag storage, and definer-cache objects. The implementation that fills and allocates definers lives in the HWS definer code, while this header is the central contract consumed by match templates, matchers, and rule insertion.

## Important APIs, types, and functions
The largest API surface is `enum mlx5hws_definer_fname`, which enumerates matchable fields across outer and inner Ethernet/IP/L4 headers, tunnel protocols, GTP/GRE/Geneve/VXLAN, flex parsers, metadata registers, MPLS, ICMP, IPsec, packet type, tunnel header dwords, and integrity bits. `enum mlx5hws_definer_match_criteria`, `enum mlx5hws_definer_type`, and `enum mlx5hws_definer_match_flag` describe match namespaces, ordinary versus jumbo definers, and protocol-specific layout flags.

`struct mlx5hws_definer_fc` is the field-copy descriptor used when creating tags: it carries source offsets and masks in PRM match parameters, destination byte/bit positions in the HWS tag, the logical field name, and callbacks for setting value and mask bits. `struct mlx5hws_definer` stores the final hardware object identity, definer type, DW and byte selectors, and the generated match mask. Cache types `mlx5hws_definer_cache` and `mlx5hws_definer_cache_item` let contexts reuse equivalent definer objects under the context control lock.

Exported helpers include `mlx5hws_definer_create_tag()`, `mlx5hws_definer_mt_init()`, `mlx5hws_definer_mt_uninit()`, `mlx5hws_definer_get_obj()`, `mlx5hws_definer_free()`, `mlx5hws_definer_calc_layout()`, `mlx5hws_definer_compare()`, `mlx5hws_definer_get_id()`, and `mlx5hws_definer_fname_to_str()`.

## Control flow
This header has no runtime body, but it defines the data path used by matcher and rule code. A match template carries a PRM mask; definer initialization converts that mask into field-copy descriptors and a compact hardware definer. Rule insertion later calls `mlx5hws_definer_create_tag()` with match values and the template's `fc` array to produce the STE tag written into hardware. Matcher resize validation compares definer layouts through `mlx5hws_definer_compare()` so rules can be moved only between equivalent matchers.

## State and persistence behavior
Runtime state is represented by cached definer objects and their firmware object IDs. A definer's hardware object persists until the context frees the cache entry or uninitializes the match template. The header also defines in-memory layouts for high-level parsed headers, but those are interpretation structures for PRM-format buffers rather than standalone persistent state.

## Dependencies and integration points
`definer.h` depends on rule tag storage from `rule.h`, command/object allocation paths, PRM match parameter layout, and HWS context locking. It is included through `internal.h` by matcher, rule, action, debug, and BWC code. Its field names are tightly coupled to firmware PRM selectors and Linux flow-match structures, so changes require cross-checking `mlx5_ifc_*` bit layouts and match criteria enable handling.

## Risks and edge cases
Selector limits are strict: ordinary match definers have limited DW/byte selectors and jumbo definers use larger tags. A wrong field offset, mask, selector, or bit order can silently steer traffic incorrectly. Protocol aliases such as Ethernet type versus IP version are later checked by `rule.c`, but this header is where those fields are named. Cache refcounts must remain aligned with firmware object lifetime, and adding new fields requires verifying hardware support, PRM layout, string conversion, and tag creation callbacks.

## Test signals
Useful signals are kernel build coverage, creating matchers for each criteria block, rules matching outer/inner IPv4 and IPv6, tunnel matches for VXLAN/Geneve/GRE/GTPU, jumbo match templates, flex parser fields, register matches, matcher resize between equivalent and non-equivalent definers, and negative tests for unsupported or too-large layouts.
