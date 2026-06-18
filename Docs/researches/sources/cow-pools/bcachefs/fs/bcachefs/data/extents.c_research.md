# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.c

Core extent and pointer utility implementation: read-device selection, btree pointer validation, extent merging, CRC packing, pointer mutation, durability accounting, cached pointer cleanup, validation, text formatting, endian swabbing, extent flags, and key cutting.

Key entry points and areas:
- Read selection: `bch2_bkey_pick_read_device()` chooses a readable pointer considering failed devices, checksum retries, EC reconstruction, preferred device flags, device latency, and forced debug modes.
- Validation/text: `bch2_bkey_ptrs_validate()`, `bch2_btree_ptr_validate()`, `bch2_btree_ptr_v2_validate()`, and text helpers validate/format pointers, CRCs, EC entries, reconcile entries, and btree pointers.
- Merge/cut: `bch2_extent_merge()`, `bch2_reservation_merge()`, `bch2_cut_front_s()`, and `bch2_cut_back_s()` combine or trim keys while preserving pointer/CRC semantics.
- CRC helpers: `bch2_extent_crc_append()`, `bch2_bkey_narrow_crc()`, and packing helpers select crc32/crc64/crc128 entry formats based on checksum width, size, and nonce.
- Pointer mutation: drop pointer/device/EC helpers, append decoded pointers, cached pointer marking, stale cached pointer dropping, extra durability dropping.
- Accounting: dirty pointer counts, allocated pointer counts, compressed sectors, incompressible propagation, replica/durability calculations, readability tests.

Important invariants:
- Direct extents cannot contain duplicate device pointers, mixed written/unwritten pointers, redundant CRC/stripe entries, cached+EC pointers, or all-invalid dirty pointer sets at commit.
- Pointer validation checks device existence when possible, bucket bounds, and that pointers do not span buckets.
- Extent merge refuses to cross buckets, merge incompatible compression/nonce/EC metadata, or exceed encoded extent size/CRC field limits.
- Cached pointers are limited to one suitable non-stale pointer and are incompatible with EC.
- EC durability may be reduced by dropping EC metadata only when online durability remains sufficient.

Dependencies and interactions:
- Central dependency for read/write, compression, checksum, EC, reconcile, allocator accounting, fsck validation, btree pointer handling, and debug trace output.
