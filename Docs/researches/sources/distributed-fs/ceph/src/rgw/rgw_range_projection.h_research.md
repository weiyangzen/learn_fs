# sources/distributed-fs/ceph/src/rgw/rgw_range_projection.h

## Purpose

Provides stateless helpers that project requested plaintext object byte ranges onto compressed or encrypted on-disk byte ranges. It lets GET paths fetch the minimum required stored bytes while preserving enough skip/block metadata for decompression or decryption filters.

## Important APIs, Types, and Functions

`DiskRange` stores disk offset/end, first-block plaintext skip, original request length, and encryption block start skip. `DecompressRange` extends it with compression block indices and plaintext query offset/length. `project_compress_range()` maps plaintext ranges to compression blocks. `find_part_for_offset()` locates which encrypted multipart part contains a plaintext offset. `project_encrypt_range()` maps plaintext ranges to encrypted byte ranges for single-part and multipart objects.

## Control Flow and Data Flow

Compression projection uses binary search over `RGWCompressionInfo::blocks` for partial content and full first/last block selection for whole-object reads. It returns the compressed disk span from first block `new_ofs` through last block end, and records how many decompressed bytes to skip.

Encryption projection aligns plaintext start and end to encryption block boundaries, converts them with `crypt_logical_to_enc_offset()` and `crypt_align_enc_block_end()`, and clamps to encrypted object or part sizes. Multipart projection first finds start and end parts by converting encrypted part lengths back to plaintext sizes, then computes cumulative encrypted offsets.

## State and Persistence Behavior

No state is stored. The functions rely on persisted compression block maps, encrypted object total size, and multipart encrypted part lengths passed by the caller.

## Dependencies and Integration Points

Depends on `rgw_compression_types.h` for compression block metadata and `rgw_crypt.h` for encryption offset conversion helpers. Integrated into RGW GET range handling for compressed and encrypted objects.

## Risks and Edge Cases

`project_compress_range()` assumes `cs_info.blocks` is non-empty and sorted by plaintext offset. `r.length = end + 1 - ofs` assumes valid inclusive ranges. Multipart encryption projection assumes `parts_len` is non-empty when using multipart and that `end_part_idx` remains valid; clamping behavior around last part is subtle. `block_size` should be a power of two because bit masks are used for alignment.

## Test Signals

Cover full-object and partial compressed ranges, single-block and multi-block compressed reads, empty block vectors as invalid input, encrypted single-part first/middle/last block ranges, encrypted object-size clamping, multipart ranges within one part and crossing parts, range ending at a part boundary, and invalid or zero block sizes.
