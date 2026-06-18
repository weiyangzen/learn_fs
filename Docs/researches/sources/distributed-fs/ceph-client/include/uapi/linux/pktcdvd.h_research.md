<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h

Purpose: defines the control ABI for the packet-writing block layer used with ATAPI/SCSI CD-R, CD-RW, DVD-R, and DVD-RW devices.

Important APIs and types: constants describe writer limits, packet buffering, device types (`PACKET_CDR*`, `PACKET_DVDR*`), media/status flags, disc/session states, and mode/block encodings. `struct pkt_ctrl_command` carries setup, teardown, and status requests with source device, packet device, device index, and device count. `PACKET_CTRL_CMD` is the only ioctl, encoded with magic `'X'`.

Control flow: userspace opens the packet control device and issues `PKT_CTRL_CMD_SETUP`, `PKT_CTRL_CMD_TEARDOWN`, or `PKT_CTRL_CMD_STATUS`; the kernel creates/removes packet devices or reports mapping state.

State and persistence: runtime state is packet-device binding, writer slots, buffered packet data, and optical media state. The header exposes control fields only; media contents are persisted by the underlying optical device.

Dependencies and integration points: depends on Linux integer types and ioctl encoding. Integrates with the block layer, cdrom/scsi drivers, packet writing module, and userspace tools managing `/dev/pktcdvd`.

Risks and test signals: risks include stale device numbers, old 32-bit `dev_t` encoding, teardown while I/O is active, and media-state/reporting mismatches. Test setup/status/teardown, max writer handling, invalid device indices, writable/non-writable media, and module unload with open packet devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pktcdvd.h -->
