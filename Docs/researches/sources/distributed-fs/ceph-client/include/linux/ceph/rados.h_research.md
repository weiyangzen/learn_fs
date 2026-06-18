# sources/distributed-fs/ceph-client/include/linux/ceph/rados.h

## Purpose

`rados.h` defines shared RADOS object-store wire constants and operation formats: FSIDs, snapshots, time encoding, placement/pool/OSD flags, stable PG modulo, object operation codes, op mode/type helpers, op flags, xattr/watch/copy/backoff enums, and packed OSD op payload structs.

## Important APIs, Types, and Functions

Important types are `ceph_fsid`, `ceph_timespec`, `ceph_pg_v1`, `ceph_object_layout`, `ceph_eversion`, and `ceph_osd_op`. Important helpers/macros include `ceph_fsid_compare()`, `ceph_stable_mod()`, `__CEPH_FORALL_OSD_OPS`, generated `CEPH_OSD_OP_*` enum values, op type/mode helper functions, `ceph_osd_op_name()`, and `ceph_osd_watch_op_name()`.

## Control Flow

There is little executable flow beyond classification helpers. OSD-client code selects opcodes and flags, fills `ceph_osd_op` union fields according to opcode class, then sends them in OSD request messages. Stable modulo controls PG remapping behavior as PG counts grow.

## State and Persistence Behavior

The file owns no mutable state. Constants and packed structs are durable wire/storage ABI. Snapshot sentinels such as `CEPH_NOSNAP` and pool/OSD flags are interpreted by OSDs and clients across releases.

## Dependencies and Integration Points

It includes `msgr.h` and integrates with `osd_client.h`, `osdmap.h`, CephFS layouts, RBD-like object users, and user-space librados-compatible operation semantics.

## Risks and Edge Cases

The warning against using raw opcodes matters because some op behavior was redefined and helpers special-case `CALL`. Packed union interpretation must match opcode. Stable modulo requires a power-of-two-minus-one mask. Error aliases like `EOLDSNAPC` and `EBLOCKLISTED` map Ceph semantics onto Linux errno values.

## Test Signals

Check opcode/name tables, op type/mode helpers including `CALL`, packed struct layout, stable modulo vectors across PG-count transitions, watch/copy/xattr flag encoding, and mixed-version OSD operation compatibility.
