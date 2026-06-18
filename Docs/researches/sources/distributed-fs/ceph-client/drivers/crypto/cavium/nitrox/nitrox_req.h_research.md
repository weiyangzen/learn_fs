# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_req.h

## Purpose

`nitrox_req.h` defines the Nitrox SE request ABI shared between Crypto API front ends and the request manager. It contains firmware/hardware descriptor formats, crypto context layout, request context structures for skcipher/AEAD variants, scatter-gather component formats, completion markers, and helper routines that build request-local source/destination SG arrays with IV, output response header, and completion bytes.

## Important APIs, Types, And Functions

- `PENDING_SIG` is written to ORH/completion memory before submission and later polled by completion handling.
- `PRIO` is the Crypto API priority used by Nitrox algorithms.
- `struct gphdr`, `union se_req_ctrl`, and `struct se_crypto_request` describe the logical SE firmware request.
- `enum flexi_cipher`, `enum flexi_auth`, `union fc_ctx_flags`, and `struct flexi_crypto_context` define firmware context fields for cipher/auth choices, AES key length, IV source, MAC length, and keys.
- `struct crypto_ctx_hdr`, `struct ctx_hdr`, and `struct nitrox_crypto_ctx` bridge software context memory to DMA context handles.
- `struct nitrox_kcrypt_request`, `struct nitrox_aead_rctx`, and `struct nitrox_rfc4106_rctx` are per-request contexts used by algorithm implementations.
- `union pkt_instr_hdr`, `union pkt_hdr`, `union slc_store_info`, `struct nps_pkt_instr`, and `struct aqmq_command_s` model packet and AQM hardware command words with endian-specific bitfields.
- `struct nitrox_sgcomp` stores four DMA pointer/length pairs per component; `struct nitrox_sgtable` tracks mapped SG state and component DMA address.
- `struct resp_hdr` and `struct nitrox_softreq` are request-manager state for posted commands, response/backlog lists, DMA mappings, timestamps, and callbacks.
- Helpers such as `flexi_aes_keylen()`, `alloc_req_buf()`, `create_single_sg()`, `create_multi_sg()`, `set_orh_value()`, `set_comp_value()`, `alloc_src_req_buf()`, `nitrox_creq_set_src_sg()`, `alloc_dst_req_buf()`, `nitrox_creq_set_orh()`, `nitrox_creq_set_comp()`, and `nitrox_creq_set_dst_sg()` are used by skcipher/AEAD request preparation.

## Control Flow

Algorithm front ends allocate request-local buffers using `alloc_src_req_buf()` and `alloc_dst_req_buf()`. Source layout is IV bytes followed by source SG entries; destination layout is ORH, IV, destination SG entries, and completion bytes. The front end fills `se_crypto_request` fields, including opcode, GP header offsets, context handle, control flags, and source/destination SG pointers. `nitrox_reqmgr.c` then maps those SG lists, converts them into Nitrox SG components, constructs a 64-byte `nps_pkt_instr`, posts it to a packet input queue, and later polls ORH/completion bytes.

## State And Persistence Behavior

Most data defined here is transient request or transform state. Transform state includes DMA-backed flexi crypto context memory and key material; exit paths must clear it. Request state includes dynamically allocated SG arrays, ORH/completion markers, and soft request mappings. Hardware-visible state is stored in big-endian descriptor fields and DMA memory. The helpers set `PENDING_SIG` via `WRITE_ONCE()` so completion polling can observe hardware writes reliably.

## Dependencies And Integration Points

The header depends on Linux DMA mapping, scatterlist, Crypto API AES constants, and Nitrox device definitions. It integrates with `nitrox_skcipher.c`, `nitrox_aead.c`, and `nitrox_reqmgr.c`. Endian-specific bitfields are part of the hardware ABI, so CPU endian definitions must match descriptor construction.

## Risks And Edge Cases

- Request buffers combine raw byte headers and `struct scatterlist` arrays; alignment and size assumptions must remain valid.
- `create_multi_sg()` uses `sg_virt()` from source SG entries, so callers must provide CPU-addressable SGs for this synthetic SG construction stage.
- `u16 total_bytes` in `nitrox_sgtable` can represent only limited input length; large requests need scrutiny.
- Bitfield layouts are compile-time endian-dependent and fragile if moved across architectures or changed without matching hardware docs.
- `PENDING_SIG` collision with a legitimate ORH/completion value would confuse completion polling, though the all-ones marker is chosen as a sentinel.

## Test Signals

Test signals include correct descriptor bytes under big/little endian builds, skcipher and AEAD known-answer tests, SG layouts with fragmented input/output, in-place and out-of-place CBC IV handling, timeout behavior when completion markers are not updated, and KASAN/KMSAN coverage for request buffer sizing.
