# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_stream.h

Purpose: This header documents and defines the command stream extension-header format used when userspace submits Rogue commands to the kernel. It separates fixed main-stream data from optional BRN/ERN extension data.

Important APIs/types/functions: Header fields are `PVR_STREAM_EXTHDR_TYPE_SHIFT`, `PVR_STREAM_EXTHDR_TYPE_MASK`, `PVR_STREAM_EXTHDR_TYPE_MAX`, `PVR_STREAM_EXTHDR_CONTINUATION`, and `PVR_STREAM_EXTHDR_DATA_MASK`. Per-DM extension type/valid masks currently define geometry type 0 with BRN49927, fragment type 0 with BRN47217/BRN49927 but valid mask only BRN49927, and compute type 0 with BRN49927.

Control flow: Parsing flow is specified in comments: a command stream starts with a 64-bit length/padding header, then main stream data, then optional extension headers and extension payloads. Each extension header carries type, continuation, and quirk/enhancement bitmask; parsing continues while the continuation bit is set. Extension parameters override duplicate main-stream parameters.

State and persistence behavior: The header has no state. Parsed stream data becomes transient submission data and may be copied into persistent client CCB command structs.

Dependencies and integration points: No includes in the file itself; it assumes `BIT` is available via inclusion context. It integrates with userspace command builders, kernel stream parsers/validators, `pvr_rogue_fwif_dev_info.h` BRN/ERN capability indices, and client command structs.

Risks: Parser and producer must agree on natural alignment and reserved-zero bits. The fragment valid mask excluding BRN47217 despite defining the bit is a compatibility detail that should be reviewed before enabling. Bad length or continuation handling can overrun streams or ignore required workaround data.

Test signals: Stream parser unit tests for main-only, single-extension, multi-header continuation, reserved bits, invalid type, duplicate override behavior, natural alignment, and BRN49927/BRN47217 feature-specific command packing.
