# sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.c

## Purpose
`blockcheck.c` computes and validates OCFS2 metadata integrity fields: CRC32 plus a Hamming-code ECC capable of correcting a single bit error. It also exposes optional debugfs counters for checked blocks, checksum failures, and ECC recoveries.

## Important APIs, types, and functions
Low-level Hamming APIs are `ocfs2_hamming_encode`, `ocfs2_hamming_encode_block`, `ocfs2_hamming_fix`, and `ocfs2_hamming_fix_block`. Block APIs are `ocfs2_block_check_compute`, `ocfs2_block_check_validate`, `ocfs2_block_check_compute_bhs`, and `ocfs2_block_check_validate_bhs`. Superblock-gated wrappers are `ocfs2_compute_meta_ecc`, `ocfs2_validate_meta_ecc`, `ocfs2_compute_meta_ecc_bhs`, and `ocfs2_validate_meta_ecc_bhs`. Debugfs wrappers install/remove `blockcheck` statistic files.

## Control flow
Compute paths zero the embedded `struct ocfs2_block_check`, calculate CRC32 over disk-endian data, compute Hamming parity, then write little-endian check fields. Validate paths save stored CRC/ECC, zero the field, recalculate CRC, and return success if it matches. On mismatch they increment failure counters, compute current ECC, apply `stored_ecc ^ current_ecc` as the bit fix, then re-run CRC; success increments recovery, failure returns `-EIO`. Multi-buffer variants stream CRC/ECC across buffer heads with bit offsets.

## State and persistence behavior
Persistent state is the on-disk `ocfs2_block_check` embedded in metadata blocks. Runtime state consists of optional `ocfs2_blockcheck_stats` counters protected by a spinlock and debugfs dentries. Validation temporarily mutates the in-memory block while zeroing/restoring check fields and may correct the data buffer in place.

## Dependencies and integration points
It depends on Linux CRC32, bitops, buffer heads, debugfs, endian helpers, and OCFS2 superblock feature tests. Metadata readers/writers call the high-level wrappers so ECC is active only when `ocfs2_meta_ecc()` is enabled.

## Risks and test signals
Risks include corrupting buffers when an uncorrectable error is treated as correctable, wrong bit numbering across multi-buffer metadata, missing restoration of check fields, counter wrap, and callers passing host-endian instead of disk-endian data. Test signals include clean CRC fast path, single-bit correction, multi-bit failure, split buffer-head metadata, disabled meta-ECC feature, debugfs counter reads, and fuzzed block sizes up to the 4 KiB ECC assumption.
