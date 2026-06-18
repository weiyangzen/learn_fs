# sources/distributed-fs/ceph-client/include/xen/interface/io/blkif.h

Purpose: defines the Xen block frontend/backend ring ABI for virtual disks, including request operations, scatter/gather segment layout, indirect descriptors, response statuses, and virtual disk flags.

Important APIs/types/functions: `blkif_vdev_t`, `blkif_sector_t`, operations `BLKIF_OP_READ`, `BLKIF_OP_WRITE`, `BLKIF_OP_WRITE_BARRIER`, `BLKIF_OP_FLUSH_DISKCACHE`, `BLKIF_OP_DISCARD`, and `BLKIF_OP_INDIRECT`; `struct blkif_request_segment`, request variants `blkif_request_rw`, `blkif_request_discard`, `blkif_request_other`, `blkif_request_indirect`, `struct blkif_request`, `struct blkif_response`, `BLKIF_RSP_*`, `DEFINE_RING_TYPES(blkif, ...)`, and `VDISK_*`.

Control flow: the frontend publishes one or more shared rings and event channels in XenStore, optionally using multi-queue and multi-page ring keys. It enqueues read/write/discard/flush/indirect requests with grant refs to data pages. The backend maps grants, performs storage I/O, and returns a response with the echoed `id`, operation, and status.

State and persistence: request state lives in shared rings. `id` is frontend-private correlation state. Grant references for data and indirect pages remain valid until the backend consumes them. XenStore feature keys persist for the device lifetime.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus, event channels, backend storage drivers, discard/flush/barrier feature discovery, and Linux-style virtual disk numbering.

Risks: packed layout and `CONFIG_X86_32` padding preserve ABI offsets; changing them breaks mixed ABI pairs. Feature nodes are advisory; operations may still return `BLKIF_RSP_EOPNOTSUPP`. Indirect segment counts must be bounded by backend-advertised limits.

Test signals: block I/O read/write integrity, flush/discard/barrier fallback paths, multi-queue setup, indirect I/O above 11 segments, grant leak checks, and ABI size/offset assertions on 32-bit and 64-bit builds.
