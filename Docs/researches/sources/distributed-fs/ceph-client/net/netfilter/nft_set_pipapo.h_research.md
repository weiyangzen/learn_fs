
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h

## Purpose

`nft_set_pipapo.h` defines the shared constants, data structures, sizing logic, and generic inline bucket operations for the PIPAPO set backend and its AVX2 companion.

## Important APIs, Types, and Functions

Key constants define maximum fields, minimum concatenation count, maximum field bytes, four-bit/eight-bit group widths, lookup-table size thresholds, mapping-table bit packing, and alignment headroom. Core types include `union nft_pipapo_map_bucket`, `struct nft_pipapo_field`, `struct nft_pipapo_scratch`, `struct nft_pipapo_match`, `struct nft_pipapo`, and `struct nft_pipapo_elem`. Shared helpers include `pipapo_refill()` declaration, `pipapo_and_field_buckets_4bit()`, `pipapo_and_field_buckets_8bit()`, `pipapo_estimate_size()`, and `pipapo_resmap_init()`.

## Control Flow

The header's inline matching helpers walk lookup-table groups and intersect the current result bitmap with the bucket selected by input bytes. Sizing estimates iterate set fields and compute worst-case rule expansion and mapping cost. Alignment macros become AVX2-aware when included after `nft_set_pipapo_avx2.h`.

## State and Persistence Behavior

The structures define all durable PIPAPO state: active and clone match pointers, per-field lookup/mapping tables, per-CPU scratch maps, and GC queues. Scratch `map_index` persists per CPU to alternate two working maps between lookups.

## Dependencies and Integration Points

The header depends on nf_tables register counts, IPv6 address sizing, bit operations, and optional architecture alignment. It is included by both generic and AVX2 implementations and must keep layout compatible with nf_tables element private casting.

## Risks and Test Signals

Risks include integer overflow in size estimates, layout drift that breaks `offsetof(..., priv) == 0` assumptions, wrong bucket grouping math, and alignment mismatches between generic and AVX2 code. Test build coverage across 32-bit and 64-bit, x86-64 AVX2 and non-AVX2, large field counts, IPv6-sized fields, and estimator/backend selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.h -->
