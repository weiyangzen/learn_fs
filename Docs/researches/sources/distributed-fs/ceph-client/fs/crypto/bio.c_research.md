# sources/distributed-fs/ceph-client/fs/crypto/bio.c

Purpose: provides block-device oriented fscrypt helpers for decrypting completed read bios and writing encrypted zero ranges.

Important APIs/functions: `fscrypt_decrypt_bio()` iterates all folios in a read bio and calls `fscrypt_decrypt_pagecache_blocks()`, setting `bio->bi_status` on failure. `fscrypt_zeroout_range()` writes ciphertext blocks that decrypt to zero for a logically and physically contiguous encrypted file range. `fscrypt_zeroout_range_inline_crypt()` handles inline-crypto in the block layer using zero pages and `fscrypt_set_bio_crypt_ctx()`.

Control flow: read completion workqueues call `fscrypt_decrypt_bio()` after disk I/O has filled page-cache folios. Zeroout chooses inline crypto when configured for the inode; otherwise it allocates bounce pages, encrypts zero data unit by data unit with `fscrypt_crypt_data_unit()`, submits synchronous write bios, resets and reuses the bio until the range is complete, then frees pages.

State and persistence: transient bios, pages, completions, and status. Persistent result is encrypted zero blocks on disk.

Dependencies/integration: depends on block layer bios, folio iteration, fscrypt inode info, inline-crypto helpers, bounce-page pool from `crypto.c`, and filesystem `s_bdev`.

Risks: caller must pass block-aligned, contiguous ranges and a filesystem with one block device. Bounce-page allocation requires the filesystem to set `needs_bounce_pages` if using non-inline zeroout. Inline bio completion must aggregate errors correctly. Data unit size and sector advancement must remain aligned.

Test signals: decrypt multi-folio bios, injected crypto failure mapping to blk_status, zero-length zeroout, inline and software zeroout, ranges crossing page boundaries, allocation failure for optional pages, submit_bio_wait errors, and ciphertext verification by reading zeros back.
