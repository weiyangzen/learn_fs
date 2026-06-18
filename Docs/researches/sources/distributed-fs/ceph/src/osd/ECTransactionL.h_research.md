# sources/distributed-fs/ceph/src/osd/ECTransactionL.h

Purpose: `ECTransactionL.h` declares the legacy EC transaction planner/generator. It builds stripe-aligned legacy write plans and exposes the function that emits per-shard ObjectStore transactions.

Important APIs and types: `ECLegacy::ECTransactionL::WritePlan` tracks whether cache invalidation is needed, per-object `to_read`, `will_write`, and object/source `HashInfoRef`s. Template `get_write_plan` walks a `PGTransaction`, queries hinfo, computes projected size, read-before-write extents, write extents, truncation effects, and clone/source invalidation. `generate_transactions` is the implementation entry point.

Control flow: planning is performed with `safe_create_traverse`, preserving transaction object order. It reads hinfo for each object, handles delete-first and source operations, detects unaligned truncate/write head and tail stripes that need reads, records write extents rounded to stripe width, extends truncates with zero writes, and updates projected hinfo size.

State and persistence: the plan itself is in-memory. It prepares hinfo changes that the `.cc` later persists as the `hinfo_key` attr and identifies partial extents that must be read before legacy writes can be encoded.

Dependencies and integration: depends on `ECUtilL`, `ECExtentCacheL`, erasure-code interfaces, ObjectStore transactions, and `PGTransaction`. It is used by legacy EC backend paths selected through `ECSwitch` when EC optimizations are disabled.

Risks: the template relies on the supplied `get_hinfo` callback returning stable shared `HashInfo` objects. It aborts if `CloneRange` remains in buffer updates. It assumes stripe-aligned projected sizes after planning and disallows reading from objects that are being renamed/cloned.

Test signals: plan tests should inspect `to_read`, `will_write`, projected hinfo size, invalidation, and source hinfo handling for unaligned writes, truncates, deletes, clones, renames, and sparse appends.
