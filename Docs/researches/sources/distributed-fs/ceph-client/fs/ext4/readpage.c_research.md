# sources/distributed-fs/ceph-client/fs/ext4/readpage.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/readpage.c` implements ext4 buffered read and readahead bio assembly for pages/folios without buffer heads in the common contiguous-block case. It also manages post-read processing for fscrypt decryption and fsverity verification. The source was read as a complete 455-line file.

## Important APIs, Types, and Functions

Public entry points are `ext4_read_folio()`, `ext4_readahead()`, `ext4_init_post_read_processing()`, and `ext4_exit_post_read_processing()`. Internal post-read state is `struct bio_post_read_ctx`, with step bits from `enum bio_post_read_step`: `STEP_DECRYPT` and `STEP_VERITY`. Main helpers include `ext4_mpage_readpages()`, `mpage_end_io()`, `bio_post_read_processing()`, `decrypt_work()`, `verity_work()`, `__read_end_io()`, `bio_post_read_required()`, `ext4_set_bio_post_read_ctx()`, and `ext4_readpage_limit()`.

## Control Flow

`ext4_read_folio()` first handles inline data through `ext4_readpage_inline()`. For non-inline reads inside file size, it obtains fsverity info and triggers fsverity metadata readahead, then calls `ext4_mpage_readpages()` for one folio. `ext4_readahead()` skips inline-data files, optionally gets fsverity info, performs fsverity readahead, and passes the readahead control to the same mpage helper.

`ext4_mpage_readpages()` iterates folios from either readahead or a single-folio caller. It refuses folios that already have buffer heads and falls back to `block_read_full_folio()` for unusual layouts. For each folio it uses cached and fresh `ext4_map_blocks()` results to identify mapped contiguous blocks, records the first hole, zeroes holes at EOF or in fully sparse folios, sets mapped-to-disk when fully mapped, and batches contiguous physical blocks into read bios. If a folio has a hole followed by data, non-contiguous blocks, existing buffers, or a mapping error, the code submits any pending bio and falls back to buffer-head read or zero/error handling.

Bio completion runs through `mpage_end_io()`. If fscrypt or fsverity post-read work is required and the bio succeeded, `bio_post_read_processing()` advances steps in order. Decryption is queued to the fscrypt decrypt workqueue. Verity is queued to the fsverity workqueue and frees the mempool context before verification to avoid recursive allocation deadlocks. `__read_end_io()` ends all folio reads with success or failure, frees the post-read context if still attached, and releases the bio.

## State and Persistence Behavior

This file does not modify persistent filesystem metadata. It populates page-cache folios from disk, zero-fills holes, sets folio uptodate or error state through `folio_end_read()`, sets `folio_set_mappedtodisk()` for fully mapped folios, and attaches transient post-read contexts to bios. The post-read context cache and mempool are global runtime resources sized by `NUM_PREALLOC_POST_READ_CTXS`.

## Dependencies and Integration Points

Dependencies include `ext4_map_blocks()`, inline-data read helpers, buffer-head fallback read, folio and readahead APIs, bio allocation/submission, blk-crypto submission, fscrypt bio crypt contexts and decryption workqueues, fsverity info/readahead/verification, and ext4 read tracepoints. The code is wired into ext4 address-space operations through read_folio and readahead hooks.

## Risks and Edge Cases

The optimized path deliberately handles only simple contiguous mappings. Correct fallback is required for blocksize smaller than page size, holes before later mapped blocks, non-contiguous extents, existing buffers, and mapping errors. Verity changes the read limit to `s_maxbytes` so metadata beyond `i_size` can be verified correctly. Post-read ordering must decrypt before verity. The mempool free-before-verity behavior is important because fsverity may initiate nested reads that also need decryption contexts.

## Test Signals

Tests should cover reads and readahead of contiguous files, sparse files with EOF holes, hole-then-data layouts that force fallback, inline data, encrypted files, verity files, encrypted verity files, mapping EIO, folios with preexisting buffers, and large folios. Signals include `trace_ext4_read_folio`, successful folio uptodate state, correct zero-filled holes, fscrypt/fsverity failure propagation, and no mempool deadlocks under nested verity metadata reads.
