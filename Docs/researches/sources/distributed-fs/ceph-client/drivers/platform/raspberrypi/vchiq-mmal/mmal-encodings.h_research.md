# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-encodings.h

Purpose: MMAL encoding, image format, audio format, H.264 variant, and colorspace FourCC constants.

Important APIs, types, and functions: defines codec encodings such as H264/H263/MP4V/MJPEG/JPEG/PNG; raw image formats such as I420/YV12/YUYV/NV12/RGBA/BGRA/RGB variants; VideoCore-specific `MMAL_ENCODING_YUVUV128`, `MMAL_ENCODING_OPAQUE`, and `MMAL_ENCODING_EGL_IMAGE`; PCM audio endian/sign variants; H.264 stream variants; and predefined color spaces such as BT.601, BT.709, JPEG JFIF, FCC, SMPTE240M, and BT.470.

Control flow: no executable flow; constants are consumed when configuring MMAL component formats and translating to/from V4L2.

State and persistence: no runtime state.

Dependencies and integration points: depends on `MMAL_FOURCC()` from `mmal-common.h` being included before or alongside this header by consumers. Integrates with MMAL firmware protocol and V4L2 format mapping tables.

Risks: constants are protocol ABI values; any typo changes firmware negotiation. Some FourCC values include spaces and lowercase letters, so style cleanup can accidentally alter ABI. Consumers must include prerequisites in the correct order because this header does not include `mmal-common.h` itself.

Test signals: static assertions or unit tests comparing expected FourCC numeric values, format-negotiation tests with VideoCore firmware, and compile tests for include ordering in all consumers.
