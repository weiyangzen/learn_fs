# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_blk.h

Purpose: defines the virtio block device ABI, including config-space fields, request header/status layout, discard/write-zeroes/secure-erase, multi-queue, cache flush, device ID, and zoned block device commands.

Important APIs/types/functions: feature bits include size/segment limits, geometry, read-only, block size, topology, multi-queue, discard, write-zeroes, secure erase, and zoned support, plus legacy barrier/SCSI/flush/config-WCE bits. `virtio_blk_config` is the packed config-space structure for capacity, limits, topology, write cache, queue count, discard/write-zeroes/secure-erase limits, and zoned characteristics. Requests start with `virtio_blk_outhdr`, use command types such as `VIRTIO_BLK_T_IN`, `OUT`, `FLUSH`, `GET_ID`, `DISCARD`, `WRITE_ZEROES`, `SECURE_ERASE`, and zone operations. Zoned structs include `virtio_blk_zone_descriptor` and `virtio_blk_zone_report`. Status bytes include OK, IOERR, UNSUPP, and zoned-specific errors.

Control flow: driver negotiates features, reads config limits, creates one or more virtqueues, and submits scatter-gather requests headed by `virtio_blk_outhdr`. The device processes data direction by command type and writes a final one-byte status. Discard/write-zeroes/secure-erase pass arrays of range descriptors. Zoned commands open/close/finish/reset/report/append zones and return zone-specific status on errors.

State and persistence: persistent state is the virtual disk content and device config. Runtime state includes queue submissions, cache state, writeback mode, multi-queue count, and zoned write pointers/open/active zone counts. The header fixes request/status layouts that must remain stable across guest/host implementations.

Dependencies and integration: includes Linux types and common virtio id/config/type headers. It integrates with guest block layers, VMM block backends, host files/devices, flush/discard plumbing, SCSI passthrough legacy behavior, and zoned block device semantics.

Risks: command `type` uses both values and legacy flag bits, so combining flags incorrectly can create invalid requests. Capacity is in 512-byte sectors while block size and topology use logical units; unit conversion bugs are common. Feature-gated config fields must not be consumed unless negotiated. Zoned commands add strict alignment/resource constraints. `write_zeroes_may_unmap` affects data persistence expectations.

Test signals: virtio-blk boot/read/write tests, feature negotiation matrix tests, flush/writeback tests, discard/write-zeroes/secure-erase tests, multi-queue I/O tests, zoned command conformance tests, status-byte error injection, and packed config layout checks.
