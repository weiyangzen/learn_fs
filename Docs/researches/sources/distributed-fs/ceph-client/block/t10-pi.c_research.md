<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/t10-pi.c -->
# sources/distributed-fs/ceph-client/block/t10-pi.c

## Purpose

`t10-pi.c` generates, verifies, and remaps T10/NVMe protection information for block I/O integrity payloads. It supports CRC64 extended PI, T10 DIF CRC, and IP checksum formats, including guard tags, application tag escape handling, reference tag validation, and reference tag remapping when requests are mapped to device LBAs.

## Important APIs, Types, And Functions

The exported block-layer entry points are `bio_integrity_generate()`, `bio_integrity_verify()`, `blk_integrity_prepare()`, and `blk_integrity_complete()`. `struct blk_integrity_iter` carries the current bio, integrity payload, integrity profile, data/protection iterators, interval bytes remaining, seed/reference value, and running checksum.

Checksum helpers are `blk_calculate_guard()`, `blk_integrity_csum_finish()`, and `blk_integrity_csum_offset()`. Tuple access helpers are `blk_integrity_copy_from_tuple()`, `blk_integrity_copy_to_tuple()`, `blk_tuple_remap_begin()`, and `blk_tuple_remap_end()`. Verification/generation functions split by tuple type: `blk_verify_ext_pi()`, `blk_verify_pi()`, `blk_verify_t10_pi()`, `blk_verify_ip_pi()`, `blk_set_ext_pi()`, `blk_set_t10_pi()`, and `blk_set_ip_pi()`.

Reference remapping is handled by `__blk_reftag_remap()`, `blk_integrity_remap()`, `blk_reftag_remap_prepare()`, and `blk_reftag_remap_complete()`.

## Control Flow

`bio_integrity_generate()` and `bio_integrity_verify()` switch on `bi->csum_type` and call `blk_integrity_iterate()`. The iterator walks data bvecs, maps each segment locally, accumulates checksums over integrity intervals, and calls `blk_integrity_interval()` when an interval completes. That interval function accounts for metadata padding before the PI tuple, maps or copies the tuple even when split across protection bvecs, verifies or writes tuple fields, advances the seed, and resets checksum state.

Verify paths compare guard tags and, when `BLK_INTEGRITY_REF_TAG` is set, compare reference tags against the seed unless the app tag escape permits bypass. Generate paths write guard, app tag zero, and reference tag from the seed.

`blk_integrity_prepare()` remaps virtual reference tags to request/device reference tags before dispatch. `blk_integrity_complete()` remaps them back after completion for the completed byte count. Already mapped integrity payloads are marked with `BIP_MAPPED_INTEGRITY` to avoid double prepare.

## State And Persistence Behavior

There is no global state. Per-I/O state lives in bio/request integrity payloads and the stack-local iterator. The persistent data is the protection information stored alongside data on the device or in integrity buffers. Prepare/complete mutate reference tags in the bio integrity payload in place.

## Dependencies And Integration Points

The file depends on `linux/t10-pi.h`, `linux/blk-integrity.h`, CRC T10 DIF, CRC64 NVMe, networking checksum helpers, bvec mapping helpers, and block request helpers from `blk.h`. It integrates with bio integrity generation/verification and request mapping in the block layer.

## Risks And Edge Cases

Split protection tuples across bvecs are a key edge case; tuple copying must preserve iterator state and copy changes back only when needed. Metadata padding before `pi_offset` must be included in checksum calculations for formats that require it. Reference tag escape semantics differ for 32-bit T10 tuples and 48-bit extended PI. Remap paths must avoid double-mapping and must process only the completed intervals on completion.

Checksum endian handling differs by checksum type: T10 CRC uses big-endian guard storage, IP checksum uses host unaligned guard access, and CRC64 uses big-endian 64-bit guard plus 48-bit reference tags.

## Test Signals

Tests should cover successful generate/verify for all checksum types, guard mismatch, reference mismatch, app/ref escape cases, nonzero `pi_offset`, split tuples across protection bvecs, multi-bvec data intervals, remap prepare/complete for partial completions, `BIP_MAPPED_INTEGRITY`, and profiles without `BLK_INTEGRITY_REF_TAG`. Expected failure signal is `BLK_STS_PROTECTION` with diagnostic logging for guard/ref errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/t10-pi.c -->
