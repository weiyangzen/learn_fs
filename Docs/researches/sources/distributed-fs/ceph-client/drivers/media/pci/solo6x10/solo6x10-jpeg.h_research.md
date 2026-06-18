<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h

## Purpose
`solo6x10-jpeg.h` provides static JPEG header data and quantization tables used by the SOLO encoder V4L2 path to prepend complete MJPEG frames to hardware JPEG entropy payloads.

## Important APIs, Types, and Functions
The header exports `jpeg_header[]`, `SOF0_START`, `DQT_START`, `DQT_LEN`, and `jpeg_dqt[4][DQT_LEN]`. There are no functions. `solo_update_mode()` in `solo6x10-v4l2-enc.c` modifies SOF0 dimensions and copies one quantization table according to `solo_g_jpeg_qp()`.

## Control Flow
The base header is copied into each `solo_enc_dev` during encoder allocation. Whenever video standard, format, or JPEG quality changes, encoder code patches width/height bytes and replaces the DQT segment before `buf_finish()` copies the header into the beginning of user buffers.

## State and Persistence
The arrays are read-only static data. Mutable state is in each encoder instance's `jpeg_header` and `jpeg_len`; no persistent data exists.

## Dependencies and Integration Points
The constants are tightly coupled to byte offsets expected by `solo6x10-v4l2-enc.c`. The hardware only supplies compressed JPEG payload data, so these software tables are required to make captured MJPEG buffers decodable by userspace.

## Risks and Edge Cases
`SOF0_START` and `DQT_START` are hard-coded offsets into `jpeg_header[]`; changing the base header without adjusting offsets would corrupt emitted MJPEG. The QP index must remain in range 0-3, as enforced by the JPEG QP helpers outside this header.

## Test Signals
Validate MJPEG buffers start with SOI/JFIF-compatible markers, dimensions match CIF/D1 and PAL/NTSC modes, DQT bytes change with JPEG QP controls, and common decoders can parse captured MJPEG frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-jpeg.h -->
