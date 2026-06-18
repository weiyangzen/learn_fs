# sources/distributed-fs/ceph-client/tools/lib/bpf/btf_relocate.c

## Purpose
`btf_relocate.c` relocates split BTF that was built against a distilled base BTF so it can instead reference a real base BTF. The output BTF keeps only split types, points at the supplied base BTF, and has its split type IDs and string offsets rewritten to the target base's numbering and string table.

## APIs, Types, and Functions
The public API is `btf_relocate(struct btf *btf, const struct btf *base_btf, __u32 **id_map)`. Internal state is carried by `struct btf_relocate`, which tracks the split BTF, real base BTF, distilled base BTF, counts for base/split/distilled types, string lengths, `id_map`, and `str_map`. Key helpers are `btf_relocate_validate_distilled_base()`, `btf_relocate_map_distilled_base()`, `btf_mark_embedded_composite_type_ids()`, `btf_relocate_rewrite_type_id()`, `btf_relocate_rewrite_strs()`, and the name/size search helpers built around `struct btf_name_info`.

## Control Flow, State, and Persistence
`btf_relocate()` rejects missing or identical base BTFs, allocates an ID map for all current types and a string map for the distilled base strings, validates that distilled base types are named int/float/enum/fwd/struct/union records, and pre-maps split IDs by adding the difference between real base and distilled base type counts. It then maps distilled base IDs to real base IDs by sorting distilled types by name and optional size, scanning real base types, handling kind compatibility, distinguishing FWD/struct/union forms, and enforcing size equality for embedded composites. After mapping, it rewrites all type-id fields in split records through `btf_field_iter`, rewrites string offsets either into the real base string table or shifted split string range, and finally calls `btf_set_base_btf()`.

## Dependencies and Integration
This file shares code between libbpf userspace and kernel builds through conditional macro aliases for BTF accessors, allocation, sorting, and bsearch support. It depends on `btf_iter.c` for generic ID/string field traversal and on BTF helpers for base-BTF access and header/string metadata. It integrates with split-BTF consumers that need a compact distilled base during build but a concrete runtime base for verifier or kernel use.

## Risks and Test Signals
Risks include ambiguous same-name/same-size base candidates, unmapped distilled base names, embedded struct/union size mismatches, off-by-one handling around BTF ID 0, and string remapping diagnostics that need correct old-offset reporting. Since the function mutates BTF in place and optionally transfers `id_map` ownership to the caller, failure-path cleanup and caller ownership are important. Test signals are relocation with duplicate-named base composites, embedded and pointer-only base composites, enum versus enum64 matching, module/kernel base swaps, unsupported distilled kinds, missing strings, and validation that all split record references point to valid post-relocation IDs.
