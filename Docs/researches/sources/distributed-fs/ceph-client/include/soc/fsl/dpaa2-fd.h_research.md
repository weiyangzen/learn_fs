# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-fd.h

Purpose: provides DPAA2 Frame Descriptor, scatter-gather entry, and frame-list entry layouts plus inline accessors for DPAA2 datapath hardware.

Important APIs and types: `struct dpaa2_fd` is the 32-byte frame descriptor with address, length, BPID, format/offset, frame context, control, and flow context. Masks define short-length, format, offset, BPID, final, and error/annotation bits. `enum dpaa2_fd_format`, `struct dpaa2_sg_entry` with `enum dpaa2_sg_format`, and `struct dpaa2_fl_entry` with `enum dpaa2_fl_format` describe single, SG, and frame-list forms. Inline helpers get/set addresses, lengths, offsets, formats, BPIDs, FRC, CTRL, FLC, final flags, and short-length behavior with little-endian conversion.

Control flow: DPAA2 drivers build descriptors, enqueue them to frame queues, dequeue and parse them, walk SG tables or frame lists, and use control/error bits to route completion/error handling.

State and persistence: descriptors are transient DMA-visible memory owned by drivers/hardware queues. No persistent state is stored.

Dependencies and integration points: depends on Linux types and byteorder helpers; integrates DPIO, Ethernet, crypto, and accelerator drivers.

Risks and test signals: risks include incorrect endian updates during read-modify-write, unmasked offsets/BPIDs/lengths, final-bit errors in SG/FLE chains, short-length interpretation drift, and DMA address truncation on unusual platforms. Test descriptor encode/decode round trips, SG final handling, frame-list queues, FD error bits, high DMA addresses, and compile-time layout/size checks.
