# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-cfg.h

Purpose: centralizes Delta driver limits, defaults, firmware version text, frame-buffer counts, autosuspend timing, and decoder declarations.

Important APIs and constants: defines firmware version `21.1-3`, min/max dimensions 32x32 to 4096x2400, 32-pixel frame alignment, default MJPEG-to-NV12 formats, max access units, DPB/user frame limits, max private frame data, 5 ms runtime-PM autosuspend, and `DELTA_MAX_DECODERS`. Under MJPEG configuration it declares `extern const struct delta_dec mjpegdec`.

Control flow: these constants drive V4L2 format bounding, frame size/allocation calculations, output queue buffer inflation, decoder registry sizing, and device naming.

State and persistence: no state; it establishes compile-time policy and hardware/firmware constraints consumed across the module.

Dependencies and integration points: depends on V4L2 fourcc constants and `VIDEO_MAX_FRAME` from media headers included by consumers. It is included by `delta.h`, so its values flow into every Delta implementation.

Risks: frame count is capped against `VIDEO_MAX_FRAME`, so platform assumptions can silently reduce theoretical DPB/user buffering. Defaults and limits must match firmware capabilities; mismatches can lead to rejected IPC decode requests or undersized buffers. The firmware version is only a string and does not enforce compatibility with the rpmsg firmware endpoint.

Test signals: run V4L2 try/s_fmt around min/max/unaligned sizes, output queue allocation at high DPB counts, and firmware boot against the advertised version.
