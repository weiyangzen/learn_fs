# sources/distributed-fs/ceph-client/include/media/v4l2-jpeg.h

Purpose: declares JPEG marker/header parsing structures, constants, reference Huffman/quantization tables, and `v4l2_jpeg_parse_header()` for JPEG codec drivers.

Important APIs/types: constants define component/table limits, Huffman table prefixes, reference table lengths, and 8x8 block size. `struct v4l2_jpeg_reference` points into the input buffer with start and length. Frame and scan component structs model ITU-T.81 SOF/SOS syntax. `enum v4l2_jpeg_app14_tf` records Adobe APP14 transform interpretation. `struct v4l2_jpeg_header` aggregates SOF/SOS references, DHT/DQT references and counts, parsed frame header, optional scan/quantization/Huffman output pointers, restart interval, entropy-coded segment offset, and APP14 transform flag.

Control flow: a JPEG driver initializes optional pointers in `v4l2_jpeg_header`, calls `v4l2_jpeg_parse_header(buf, len, out)`, then uses parsed dimensions, component sampling, quantization/Huffman table references, restart interval, and entropy offset to program decoder hardware. Default reference tables are available for hardware or streams that need standard tables.

State and persistence: parsed references point into the caller's buffer, so the buffer must outlive hardware setup using those references. Optional output arrays are caller-provided. No heap ownership is declared in the header.

Dependencies and integration: includes `linux/v4l2-controls.h` for JPEG chroma subsampling enum. It integrates with stateless/stateful JPEG mem2mem drivers and V4L2 JPEG controls.

Risks: references are not deep copies; malformed marker lengths can cause parser rejection and must not be bypassed; APP14 absence is represented as `V4L2_JPEG_APP14_TF_UNKNOWN`; four-component CMYK/YCCK streams need transform-aware handling; and drivers must account for missing optional scan/table storage.

Test signals: parse baseline JPEGs with one/three/four components, multiple DHT/DQT tables, restart interval, APP14 transform variants, missing optional arrays, malformed marker lengths, truncated entropy segment, and compare reference table constants against ITU-T.81 defaults.
