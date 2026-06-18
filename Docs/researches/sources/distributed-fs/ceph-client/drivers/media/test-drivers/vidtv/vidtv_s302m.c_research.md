# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.c

## Purpose
`vidtv_s302m.c` implements a virtual SMPTE 302M/AES3 audio encoder for vidtv. It produces 16-bit AES3 subframes in an MPEG private stream, either from a caller-provided sample buffer or from a built-in sine-wave melody generator. The encoder can run independently or synchronize audio access units to a video encoder's access-unit list and PTS values.

## Important APIs, Types, and Functions
The exported lifecycle is `vidtv_s302m_encoder_init()` and `vidtv_s302m_encoder_destroy()`, returning and freeing a generic `struct vidtv_encoder`. Internally, `vidtv_s302m_encode()` is installed as the encoder callback and `vidtv_s302m_clear()` resets buffered output and access units. Access-unit helpers include `vidtv_s302m_access_unit_init()`, `vidtv_s302m_access_unit_destroy()`, `vidtv_s302m_alloc_au()`, `vidtv_s302m_compute_sample_count_from_video()`, and `vidtv_s302m_compute_pts_from_video()`. Sample and frame generation happens through `vidtv_s302m_get_sample()`, `vidtv_s302m_write_h()`, `vidtv_s302m_write_frame()`, and `vidtv_s302m_write_frames()`.

## Control Flow
Encoding starts by destroying the previous access-unit list and allocating a new one. If a sync video encoder exists, one audio access unit is created for each video access unit, sample counts are derived from sample duration ratios, and PTS values are copied from video. Without sync, a single access unit is emitted using ffmpeg-derived default frame count, PTS increment, and offset. For each access unit, the encoder writes a 302M elementary-stream header, generates or reads samples, writes 5-byte AES3 frames with ffmpeg's bit-reversal table, advances offsets and counters, and records each access unit's byte size and buffer offset.

## State and Persistence
Persistent runtime state lives in `struct vidtv_s302m_ctx` and the containing `struct vidtv_encoder`: frame index within a 192-frame block, access-unit count, melody note duration/offset, source buffer offset, sample count, encoder buffer, and access-unit linked list. All state is in memory and reset by clear/destroy; no data persists across module unload. The source-buffer exhaustion callback is invoked before wrapping to offset zero.

## Dependencies and Integration Points
The file depends on kernel fixed-point sine math, allocation, vmalloc, jiffies-related utilities, endian helpers, and vidtv's generic encoder interface. It emits `PES_PRIVATE_STREAM_1`, sets `S302M` as the encoder ID, and uses `VIDTV_S302M_FORMAT_IDENTIFIER` from the header for PMT registration descriptors elsewhere. It integrates with video encoders via `args.sync` and with muxing code through the generic encoder's access-unit metadata.

## Risks and Edge Cases
The encoder assumes 16-bit samples and reads `u16` directly from `src_buf`, so callers must provide properly sized and aligned sample data. `vidtv_s302m_get_sample()` handles `src_buf_offset > src_buf_sz` as a bug and wraps, but a malformed size can still produce abrupt audio loops. Buffer writes rely on `vidtv_memcpy()` bounds behavior; output larger than `VIDTV_S302M_BUF_SZ` would truncate or warn through helpers rather than return a direct error. Sync sample-count computation uses rounded integer durations, so long runs can drift relative to video.

## Test Signals
Validation should include generated stream decoding with ffmpeg or DVB tools, PTS alignment with video access units, source-buffer wrap callback behavior, and clear/destroy leak checks. Boundary tests should stress maximum access-unit counts, no-sync mode, null source tone generation, and small destination buffer behavior through the common safe-copy wrappers.
