<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c

## Purpose

`sun4i-ss-hash.c` implements MD5 and SHA1 ahash operations for the sun4i Security System. It feeds data through the SS FIFO, preserves partial blocks and intermediate digest state, and performs software-style padding for finalization.

## Important APIs, Types, And Functions

TFM lifecycle uses `sun4i_hash_crainit()` and `sun4i_hash_craexit()`. Request APIs are `sun4i_hash_init()`, `sun4i_hash_update()`, `sun4i_hash_final()`, `sun4i_hash_finup()`, and `sun4i_hash_digest()`. Export/import helpers support MD5 and SHA1 state migration. The main worker `sun4i_hash()` handles update and final logic.

## Control Flow

Small non-final data is buffered in `op->buf`. For hardware processing, the driver restores arbitrary IV registers when continuing a previous hash, enables the SS with MD5 or SHA1 mode, streams full 32-bit words from SGs while linearizing partial bytes, and either saves intermediate digest registers or finalizes. Finalization writes remaining bytes, appends the 0x80 bit, zero padding, and bit length in SHA1 big-endian or MD5 little-endian format, sets `SS_DATA_END`, waits for completion, delays briefly, and reads digest registers.

## State And Persistence Behavior

`struct sun4i_req_ctx` stores mode, byte count uploaded to hardware, intermediate hash words, a 64-byte partial buffer, length, and flags. Runtime PM is held by the TFM. Hardware access is serialized with `ss->slock`.

## Dependencies And Integration Points

It depends on ahash internals, MD5/SHA1 state formats, SG mapping iterators, unaligned stores, SS FIFO/register definitions, runtime PM, and variant SHA1 endianness from core.

## Risks And Test Signals

Risks include padding off-by-one errors, timeout on `SS_DATA_END`, partial-SG handling bugs, export/import state mismatch, and digest endianness regressions. Test MD5/SHA1 crypto vectors across update/final/digest/export/import paths, small messages, large scatterlists, unaligned SGs, and A10/A33 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c -->
