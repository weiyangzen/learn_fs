# sources/distributed-fs/ceph-client/fs/ntfs/mst.c

## Purpose
`mst.c` implements NTFS multi-sector transfer protection. It restores sector trailer words after reads, replaces them with an update sequence number before writes, and restores the in-memory record after write submission.

## Important APIs
`post_read_mst_fixup()` validates and deprotects a protected record after disk read. `pre_write_mst_fixup()` increments the update sequence number and writes it into each 512-byte sector trailer while saving original trailers in the update sequence array. `post_write_mst_fixup()` restores original trailers without validation after a successful pre-write step.

## Control Flow and State
The functions use `usa_ofs` and `usa_count` in `struct ntfs_record`. Read fixup treats invalid/missing USA layout as unprotected and returns success, but if any sector trailer does not match the update sequence number it marks the in-memory record magic `BAAD` and returns `-EINVAL`. Pre-write fixup rejects null, `BAAD`, hole, misaligned, or size-inconsistent records, increments USN while skipping `0` and `0xffff`, stores original trailer words into the USA, and overwrites trailers with the USN.

## Dependencies and Integration
MFT mapping uses `post_read_mst_fixup()` before record validation. MFT formatting and write paths use `pre_write_mst_fixup()` before bios. The routines depend on NTFS sector size constants, record magic helpers, endian helpers, and ratelimited logging.

## Risks
The read and write functions intentionally differ: invalid USA layout is success on read but failure on write. Callers must understand that distinction. A wrong `size` or corrupt `usa_count` can silently classify data as unprotected on read. `post_write_mst_fixup()` assumes a prior successful pre-write and performs no bounds validation.

## Test Signals
Tests should include valid records, invalid USA offsets/counts, mismatched trailer words, USN wrap from `0xfffe`, records smaller/larger than 512-byte multiples, and ensuring `BAAD` is only an in-memory error signal after incomplete transfer detection.
