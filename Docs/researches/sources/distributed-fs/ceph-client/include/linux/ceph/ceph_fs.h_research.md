# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_fs.h

## Purpose

`ceph_fs.h` is the shared CephFS client/server wire-format contract for filesystem protocols. It defines protocol revisions, inode constants, file and directory layouts, auth and connection modes, message type ids, MDS states and operations, request/reply wire structs, lease/capability records, snapshots, quotas, and file lock formats.

## Important APIs, Types, and Functions

Important types include `ceph_file_layout_legacy`, `ceph_file_layout`, `ceph_dir_layout`, `ceph_mon_request_header`, `ceph_statfs`, `ceph_mds_request_head`, `ceph_mds_reply_inode`, `ceph_mds_caps`, `ceph_mds_lease`, `ceph_mds_snap_realm`, and `ceph_mds_quota`. Important helpers declared here include `ceph_file_layout_is_valid()`, layout legacy conversion helpers, `ceph_auth_proto_name()`, `ceph_con_mode_name()`, `ceph_mds_state_name()`, `ceph_session_op_name()`, `ceph_mds_op_name()`, `ceph_flags_to_mode()`, `ceph_caps_for_mode()`, and cap/lease/snap op name helpers.

## Control Flow

This header encodes protocol flow through constants and packed structs. Monitor messages request maps/statfs/auth, MDS session ops open/renew/close sessions, MDS request heads carry operation-specific union arguments, replies carry dentry/inode/cap/lease payloads, and capability messages drive grant/revoke/flush/update cycles between MDS and clients.

## State and Persistence Behavior

Most structs are `packed` little-endian ABI records sent over the wire or stored in durable metadata. `ceph_file_layout` is the in-kernel normalized layout with an RCU `pool_ns` string, while legacy layout structs preserve older on-wire forms.

## Dependencies and Integration Points

It includes `msgr.h` and `rados.h`. Integration points include the messenger message layer, monitor client, MDS client, CephFS inode/capability code, directory fragmentation, layout mapping through `striper.h`, and RADOS pool/object naming.

## Risks and Edge Cases

Changing field order, endianness, packing, enum values, or message ids is wire-incompatible. Several variable-length structs are followed by arrays/strings/blobs, so decoders must validate bounds. Legacy and extended request heads must remain compatible, and capability masks must align with MDS lock semantics.

## Test Signals

Signals include compile coverage for all CephFS protocol users, decode/encode round trips for request/reply structs, mixed-version client/server tests, layout conversion tests, MDS op name/cap mapping tests, and fuzzing of variable-length reply decoding.
