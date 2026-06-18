# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-h264.c

`coda-h264.c` contains H.264 helper logic for CODA. It parses SPS profile/level from queued decoder buffers, generates filler NAL padding, maps H.264 profile/level IDC values to V4L2 enums, and rewrites SPS frame-cropping fields for encoders whose firmware cannot emit correct crop metadata.

Public APIs are `coda_sps_parse_profile()`, `coda_h264_filler_nal()`, `coda_h264_padding()`, `coda_h264_profile()`, `coda_h264_level()`, and `coda_h264_sps_fixup()`. Static RBSP helpers read/write bits and Exp-Golomb values for SPS surgery.

Decoder queueing scans Annex B start codes until an SPS NAL and stores `profile_idc`/`level_idc` in `ctx->params`; common code then updates read-only controls and BIT decode decides whether reordering is needed. Encoder startup may call `coda_h264_sps_fixup()` for non-CODA960 unaligned visible sizes. The fixup parses SPS fields, rejects unsupported high-profile/VUI cases, computes crop units, writes crop-left/right/top/bottom plus a stop bit, and updates the SPS size.

State changes are limited to cached H.264 params or the caller-provided SPS buffer. Dependencies are vb2 buffer access, V4L2 H.264 enums, and `struct coda_ctx`. Risks are limited SPS syntax support, in-place RBSP rewriting, dependence on four-byte Annex B start codes, and needing caller-provided padding capacity. Test SPS extraction, profile/level mapping, filler sizes, crop fixups, and expected failure on unsupported SPS forms.
