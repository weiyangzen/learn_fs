# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-hdr.c

Purpose: parses enough of an MJPEG/JPEG access unit to find SOI/SOF markers and extract frame dimensions and component count for stream negotiation.

Important APIs and functions: exported function `delta_mjpeg_read_header` scans for `0xffd8` SOI followed by SOF0/SOF1 and calls internal `delta_mjpeg_read_sof`. `header_str` formats parsed header fields for debug logging.

Control flow: `delta_mjpeg_read_header` walks the input byte stream until it sees SOI, records the data offset, then requires a later SOF marker. `delta_mjpeg_read_sof` reads big-endian length/height/width plus precision and component count, bounds the component count, and ensures component metadata fits in the input before returning.

State and persistence: the parser fills the caller-provided `struct mjpeg_header` and `data_offset`. It does not allocate memory or store global state.

Dependencies and integration points: used by `delta-mjpeg-dec.c` on the first AU and every decode AU. Depends on `delta.h` for logging context and `delta-mjpeg.h` for header structures.

Risks: the parser is intentionally minimal and does not parse quantization/Huffman tables or validate all marker segment lengths. It requires SOI before SOF and returns `-ENODATA` if a partial header is supplied. Component details are not actually copied into `header->components`, only bounds-checked.

Test signals: sample MJPEG streams with SOF0/SOF1, partial/truncated buffers, SOF before SOI, component count at/above `MJPEG_MAX_COMPONENTS`, and data offset correctness for firmware decode.
