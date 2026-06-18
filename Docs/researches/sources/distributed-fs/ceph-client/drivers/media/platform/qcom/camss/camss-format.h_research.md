
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.h

## Purpose
Declares shared CAMSS format descriptors and lookup helpers for media-bus format negotiation and memory-plane layout.

## Important APIs, Types, and Functions
`struct fract` represents plane subsampling factors. `struct camss_format_info` stores media-bus code, bus bpp, V4L2 fourcc, number of planes, per-plane horizontal/vertical subsampling, and per-plane memory bits-per-pixel. `PER_PLANE_DATA()` is a designated-initializer helper for table entries. `struct camss_formats` wraps a table and count. Prototypes expose the helpers implemented in `camss-format.c`.

## Control Flow
The header is consumed by components that enumerate or choose formats. The data model lets callers derive bytesperline/sizeimage and match media-bus code to memory format.

## State and Persistence
No runtime state is stored. Constant format tables in other files provide the data.

## Dependencies and Integration Points
Depends only on Linux integer types. It integrates with V4L2 media-bus codes and pixel fourcc users across CAMSS.

## Risks and Test Signals
The plane arrays are fixed at three entries, so new formats with more planes would require ABI changes. Table correctness is critical: wrong subsampling or bpp propagates into buffer sizes and hardware stride. Compile coverage of table initializers plus format negotiation and buffer layout tests are the primary signals.
