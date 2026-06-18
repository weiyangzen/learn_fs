# sources/distributed-fs/ceph/src/osd/ECExtentCacheL.h

Purpose: `ECExtentCacheL.h` defines the legacy EC read-modify-write extent cache used by the ECLegacy pipeline to pipeline overlapping partial overwrites without dropping data needed by earlier operations. It models cached object extents as intrusive objects owned by write pins, so a cached/pending interval remains live until the write operation that completes last releases its pin.

Important APIs and types: `ECLegacy::extent_set` and `extent_map` are interval containers over logical offsets and `bufferlist` payloads. `ECExtentCacheL::write_pin` is the public pin handle. `open_write_pin`, `reserve_extents_for_rmw`, `get_remaining_extents_for_rmw`, `present_rmw_update`, and `release_write_pin` form the write pipeline contract. Internally, `extent` tracks offset, length, optional data, parent object set, and parent pin; `object_extent_set` keeps per-object intrusive sets; `pin_state` owns the list of extents pinned by a write.

Control flow: callers open a write pin, reserve write/read intervals, read only the returned missing intervals, then present read-modify-write results. `traverse_update` is the core mutation algorithm: it walks overlapping ranges, splits head/tail fragments, moves ownership to the new pin when required, and optionally replaces pending intervals with concrete buffers.

State and persistence: the cache is entirely in-memory. State lives in intrusive containers, and correctness depends on every linked `extent` being in both its object set and pin list until `release_pin` unlinks and deletes it. It persists no on-disk metadata; it protects in-flight EC overwrite state.

Dependencies and integration: this legacy cache is used from `ECCommonL`/legacy RMW code and depends on `hobject_t`, Ceph interval containers, `bufferlist`, Boost intrusive set/list, and ordered write invariants supplied by higher layers.

Risks: ownership invariants are assertion-heavy and memory-unsafe if violated; `new`/`delete` and intrusive hooks make missed unlink paths dangerous. The design assumes no concurrent read/write mix for an object and ordered writes. Any change to RMW ordering or pin lifetime can expose stale or missing buffers.

Test signals: useful tests exercise overlapping writes, pending-to-present transitions, release cleanup of empty object caches, split head/tail ranges, and assertion behavior for invalid calls such as presenting unreserved extents.
