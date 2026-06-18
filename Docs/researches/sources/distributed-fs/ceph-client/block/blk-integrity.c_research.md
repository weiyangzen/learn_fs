# sources/distributed-fs/ceph-client/block/blk-integrity.c

## Purpose
`blk-integrity.c` implements block-layer data integrity metadata support. It counts integrity scatterlist segments, maps user-provided metadata to requests, reports logical block metadata capabilities, controls integrity verification/generation sysfs flags, and enforces merge compatibility for bios and requests carrying integrity payloads.

## Important APIs, Types, and Functions
Important functions are `blk_rq_count_integrity_sg()`, `blk_get_meta_cap()`, `blk_rq_integrity_map_user()`, `blk_integrity_merge_rq()`, `blk_integrity_merge_bio()`, `blk_integrity_profile_name()`, and the `blk_integrity_attr_group`. Sysfs callbacks expose `format`, `tag_size`, `protection_interval_bytes`, `read_verify`, `write_generate`, and `device_is_integrity_capable`.

## Control Flow
`blk_rq_count_integrity_sg()` walks a bio's integrity vectors and merges adjacent physical segments subject to queue mergeability and max segment size. `blk_rq_integrity_map_user()` creates an iov iterator from a user buffer, maps it into the request bio's integrity payload, computes segment count, and sets `REQ_INTEGRITY`.

`blk_get_meta_cap()` validates the extensible ioctl, reads the disk integrity profile, and fills logical block metadata capability fields: protection interval, metadata size, PI size/offset, opaque metadata layout, checksum type, app tag size, and ref tag size. Merge checks require both sides either have no integrity or both do, then compare payload flags, app tag when checked, max integrity segment limits, and gap constraints.

Sysfs write toggles invert user-facing `read_verify`/`write_generate` values into internal `BLK_INTEGRITY_NOVERIFY` and `BLK_INTEGRITY_NOGENERATE` flags through frozen queue limits updates.

## State and Persistence
State is in `queue->limits.integrity`, per-bio `bio_integrity_payload`, request `nr_integrity_segments`, and `REQ_INTEGRITY`. Sysfs changes update queue limits rather than writing persistent media state.

## Dependencies and Integration Points
This file integrates with T10 PI/extended DIF tuple definitions, block queue limits, request/bio merging, user ioctl copy helpers, bio integrity mapping, and queue sysfs. It also gates hardware inline encryption indirectly because `blk_crypto_register()` refuses integrity-capable queues.

## Risks
Risks include mismatched metadata and data segment merging, incorrect advertised capability layout, user pointer mapping failures, and unsafe flag changes without queue freezing. The inverted sysfs flags are easy to misread: writing `1` enables verification/generation by clearing the no-verify/no-generate bit.

## Test Signals
Tests should cover segment coalescing, max segment size/limit rejection, request and bio merge compatibility, app-tag mismatch, ref-tag capability reporting for CRC/IP/CRC64, ioctl extensible-size handling, user metadata mapping failure, sysfs flag toggles, and integrity plus inline-encryption exclusion.
