# sources/distributed-fs/ceph-client/block/bio-integrity-fs.c

## Purpose

`bio-integrity-fs.c` provides filesystem-facing helpers for explicit block integrity metadata allocation, generation, verification, and freeing. It is separate from the automatic block-layer path so submitters can manage integrity around their own completion flow.

## Important APIs, Types, And Functions

`struct fs_bio_integrity_buf` embeds a `bio_integrity_payload` and one `bio_vec`, allocated from `fs_bio_integrity_pool`. Public helpers are `fs_bio_integrity_alloc()`, `fs_bio_integrity_free()`, `fs_bio_integrity_generate()`, and `fs_bio_integrity_verify()`.

## Control Flow, State, And Persistence

`fs_bio_integrity_alloc()` calls `bio_integrity_action()` and returns zero if no integrity work is needed. Otherwise it attaches an embedded payload, allocates the metadata buffer with optional zeroing, sets default integrity flags, and returns the action mask. `fs_bio_integrity_generate()` allocates and generates write metadata when needed. `fs_bio_integrity_free()` releases the buffer and container and clears `REQ_INTEGRITY`.

`fs_bio_integrity_verify()` reinitializes `bip->bip_iter` from caller-supplied sector and size, computes the integrity byte count, verifies metadata, and converts block status to errno. This is designed for submitters after driver completion.

## Dependencies And Integration Points

The file depends on `linux/blk-integrity.h`, `linux/bio-integrity.h`, common integrity helpers, and the device `blk_integrity` profile. `fs_bio_integrity_generate()` is exported for filesystem use.

## Risks And Test Signals

Callers must remember the original sector and size for verification because the bio iterator may be changed by lower layers. This path owns a single-vector mempool container and must not be mixed with user-mapped or automatic integrity ownership. Test no-action paths, PI reads/writes, iterator advancement before verification, metadata failure injection, and kmemleak/KASAN around `fs_bio_integrity_free()`.
