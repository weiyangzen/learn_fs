# sources/distributed-fs/ceph/src/osd/ECTypes.h

Purpose: `ECTypes.h` provides small EC-specific utility types shared by optimized EC code: aligned read descriptors, raw shard identifiers, and shard-indexed maps.

Important APIs and types: `ec_align_t` stores offset, size, and op flags for EC read alignment and supports equality/printing. `raw_shard_id_t` wraps an `int8_t` raw erasure-code shard index with explicit numeric conversions, increment, comparisons, assignment from int, formatter dumping, and generated test instances. `shard_id_map<T>` aliases `mini_flat_map<shard_id_t, T>`.

Control flow: no complex control flow exists. Types are value containers used in EC read/write mapping. `raw_shard_id_t` makes raw plugin chunk order distinct from logical `shard_id_t`, allowing `stripe_info_t` mapping/reverse mapping to be explicit.

State and persistence: these types hold transient in-memory descriptors. They can appear in encoded/dumped structures indirectly through users, but this header itself defines no persistent format except generated test instances and dump support for `raw_shard_id_t`.

Dependencies and integration: includes `include/types.h` for `shard_id_t` and `common/mini_flat_map.h`. Used heavily by `ECUtil`, `ECSwitch`, and optimized EC read APIs.

Risks: `raw_shard_id_t` is backed by `int8_t`, so shard counts beyond that range would be invalid. Explicit conversions reduce accidental mixing but still allow casts. `NO_SHARD` is declared here and must be defined elsewhere.

Test signals: tests should cover raw/logical shard mapping in `stripe_info_t`, comparison/increment behavior, `ec_align_t` equality, and `shard_id_map` behavior with sparse shard ids.
