# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.h

## Purpose
`vidtv_s302m.h` declares the public interface and core wire layouts for vidtv's SMPTE 302M audio encoder. It lets vidtv service setup code instantiate an audio encoder, attach it to an encoder chain, and destroy it through a type-specific wrapper.

## Important APIs, Types, and Functions
The key public type is `struct vidtv_s302m_encoder_init_args`, which carries the encoder name, optional source buffer and size, elementary-stream PID, optional video sync encoder, source-exhaustion callback, and optional chain head. `struct vidtv_s302m_ctx` is the private context used by the implementation. `struct vidtv_smpte_s302m_es` models the 302M elementary-stream header bitfield, and `struct vidtv_s302m_frame_16` holds one 5-byte encoded 16-bit AES3 frame. `vidtv_s302m_encoder_init()` returns a populated `struct vidtv_encoder`; `vidtv_s302m_encoder_destroy()` frees it.

## Control Flow
Callers pass initialization arguments to `vidtv_s302m_encoder_init()`, which allocates the generic encoder and private context, configures callbacks, stream IDs, sample rate, source buffer settings, and optional chain linkage. Later muxing code calls the generic encoder's `encode` and `clear` callbacks.

## State and Persistence
The header-defined state is per encoder instance. It tracks current AES3 frame position, total access units, melody tone state, and back-pointer to the generic encoder. All state is volatile kernel memory owned by the encoder lifecycle.

## Dependencies and Integration Points
The header includes `linux/types.h` and `vidtv_encoder.h`, binding the S302M implementation to vidtv's generic encoder abstraction and musical note enum. `VIDTV_S302M_BUF_SZ` constrains the output buffer, and `VIDTV_S302M_FORMAT_IDENTIFIER` is used for MPEG registration signaling.

## Risks and Edge Cases
Because the header exposes the private context layout, unrelated code could couple to implementation details. The initialization args do not encode ownership for `src_buf`; the implementation borrows that pointer. The source-buffer callback is optional and must tolerate repeated wrap notifications.

## Test Signals
Compile coverage should verify integration with generic encoder callers. Runtime tests should instantiate with and without `sync`, with and without `src_buf`, and confirm the configured ES PID and private stream ID are reflected in downstream PMT/PES output.
