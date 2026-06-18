<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h

Purpose: `jpeg.h` provides a static baseline JPEG header and small helper functions for GSPCA subdrivers that receive entropy-coded JPEG payloads without complete headers.

Important APIs, types, and functions: `jpeg_head[]` contains SOI, DQT, DHT, SOF0, and SOS segments unless `CONEX_CAM` is defined. `JPEG_QT0_OFFSET`, `JPEG_QT1_OFFSET`, `JPEG_HEIGHT_OFFSET`, and `JPEG_HDR_SZ` describe patch points. `jpeg_define()` copies the template and patches height, width, and Y sampling. `jpeg_set_qual()` scales luminance and chrominance quantization tables from a V4L2-style quality value.

Control flow: no runtime registration. Subdrivers allocate a header buffer of `JPEG_HDR_SZ`, call `jpeg_define()` at stream start or mode change, call `jpeg_set_qual()` when quality changes, and prepend the buffer to frame data.

State and persistence: `jpeg_head` is read-only. Mutable state lives in each subdriver's copied header buffer.

Dependencies and integration points: requires kernel `u8` and `memcpy()` availability through includers. It is used by `jeilinj.c` in this subset and by other GSPCA JPEG subdrivers.

Risks: quantization scaling does not clamp values to JPEG's usual 1..255 range, so extreme quality values can produce zero or oversized table entries if callers bypass expected ranges. Header constants must stay consistent with the byte template. Test signals include generated JPEGs decoding in userspace, correct dimensions in SOF0, and quality controls visibly changing compression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/jpeg.h -->
