# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-dec.c

Purpose: implements the Delta MJPEG decoder backend for compressed MJPEG input to NV12 output using local JPEG header parsing plus firmware IPC decode commands.

Important APIs and functions: exports `const struct delta_dec mjpegdec`. Key functions include `delta_mjpeg_open`, `delta_mjpeg_close`, `delta_mjpeg_decode`, `delta_mjpeg_get_streaminfo`, `delta_mjpeg_get_frame`, `delta_mjpeg_ipc_open`, `delta_mjpeg_ipc_decode`, and status/error formatting helpers.

Control flow: opening allocates private `delta_mjpeg_ctx`. The first `decode` call parses a JPEG header with `delta_mjpeg_read_header`, checks resolution budget, stores stream dimensions, and returns without firmware decode so V4L2 can negotiate frame info. Later decode calls lazily open a firmware instance, parse each AU header and data offset, acquire a free destination frame from the M2M queue, fill firmware JPEG decode parameters in the IPC buffer, request auxiliary decimated NV12 output with `JPEG_ADDITIONAL_FLAG_420MB`, call `delta_ipc_decode`, interpret firmware status, marks the output frame as keyframe/decoded, and exposes it through `get_frame`.

State and persistence: `delta_mjpeg_ctx` stores the parsed header, IPC handle/buffer, one pending output frame, and a large string buffer for command dumps. `delta_ctx` counters track decoded frames, stream errors, decode errors, and system errors. Firmware instance state persists until close.

Dependencies and integration points: depends on Delta V4L2 frame management, `delta-ipc`, `delta-mem`, MJPEG header parser, and firmware ABI structures from `delta-mjpeg-fw.h`.

Risks: the first AU is consumed for header discovery rather than producing output, so users must expect stream-info discovery behavior. `delta_mjpeg_ipc_decode` passes `au_dma + au_size - 1` after adding `data_offset` but does not subtract the offset from `au_size`, so the effective end address can extend past the parsed payload window. Firmware error classification distinguishes stream versus decode errors but only returns failure when IPC itself fails. Only progressive MJPEG to NV12 is implemented.

Test signals: V4L2 MJPEG header-first streaming, malformed JPEG markers, oversized resolution rejection, firmware error-code injection, NV12 payload correctness, timestamp FIFO behavior, and output frame recycling under limited capture buffers.
