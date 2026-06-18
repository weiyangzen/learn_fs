# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ni-asm.S

## Purpose
Intel SHA extension implementation of SHA-1 complete-block compression. It maps SHA-1 rounds and schedule updates onto `sha1rnds4`, `sha1nexte`, `sha1msg1`, and `sha1msg2`.

## APIs, Control Flow, And Integration
Exports `sha1_ni_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. `do_4rounds` loads and byte-swaps initial words, updates schedule words, and performs four rounds. The function loads state into `ABCD/E` register layout, saves it per block for feed-forward, emits 80 rounds via `.irp`, adds the saved state, advances input by 64 bytes, and stores the final state back in canonical order.

## State, Dependencies, Risks, And Tests
Only the caller's SHA-1 state is mutated. It depends on `<linux/linkage.h>`, SHA-NI support, and FPU bracketing in `sha1.h`. Risks are state word-order mistakes, being called without SHA-NI/FPU safety, and SHA-1 collision weakness. Tests should cover known-answer and multi-block vectors, generic comparisons, SHA-NI dispatch, and FPU-unusable fallback.
