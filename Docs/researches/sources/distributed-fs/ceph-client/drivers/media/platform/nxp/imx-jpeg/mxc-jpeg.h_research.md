# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.h

Purpose: Shared core definitions for the i.MX JPEG driver: limits, modes, format metadata, descriptor layout, queue/context/device state, encoder config ops, and parsed JPEG marker structures.

Important APIs, types, and functions: Constants define default/min/max dimensions, maximum line/stream/image sizes, plane count, pattern buffer size, and DMA alignment. `enum mxc_jpeg_enc_state` tracks encoder config versus encoding phase; `enum mxc_jpeg_mode` distinguishes decode and encode platform instances. `struct mxc_jpeg_fmt` describes raw/JPEG formats. `struct mxc_jpeg_desc` matches the hardware descriptor, including v1 encoder fields. `struct mxc_jpeg_q_data`, `struct mxc_jpeg_ctx`, `struct mxc_jpeg_slot_data`, `struct mxc_jpeg_enc_ops`, and `struct mxc_jpeg_dev` define queue, per-file, slot, version-op, and device state. SOF/SOS structs model parsed JPEG marker payloads.

Control flow: The header has no executable flow, but its structures are traversed by `mxc-jpeg.c` during open, format negotiation, parse, descriptor allocation, encode/decode submission, IRQ completion, and PM operations.

State and persistence behavior: Context state persists for an open filehandle; device state persists for the platform instance. Slot data owns coherent/SRAM descriptor and config-stream memory. Queue data stores adjusted hardware dimensions separately from visible crop dimensions, which is critical for source-change and selection behavior.

Dependencies and integration points: Includes V4L2 control/device/filehandle headers. Included by both `mxc-jpeg.c` and `mxc-jpeg-hw.h`, forming the ABI between descriptor helpers and V4L2 logic.

Risks: `struct mxc_jpeg_desc` is `__packed` and must stay exactly compatible with hardware DMA expectations. Size and alignment constants directly affect userspace buffer validation and descriptor sizing. SOF/SOS packed bitfields are endian-sensitive and are patched in-place in JPEG buffers.

Test signals: Compile-time checks indirectly verify structure visibility. Runtime encode/decode validates descriptor layout, queue adjusted dimensions, JPEG marker parsing structures, and slot allocation/free behavior. Static analysis should inspect packed bitfields and DMA descriptor writes.
