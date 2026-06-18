## sources/distributed-fs/ceph/src/rgw/rgw_mdlog_types.h

Purpose: declares metadata log sync policy and log operation status enums.

Important APIs/types: `RGWMDLogSyncType` defines how metadata sync applies remote entries: always, updates, newer-only, or exclusive. `RGWMDLogStatus` defines metadata log operation status values: unknown, write, set attributes, remove, complete, abort.

Control flow: metadata handlers and mdlog processing use these enums to choose mutation semantics and represent log lifecycle.

State and persistence: enum values are serialized indirectly through structures such as `RGWMetadataLogData`; stable numeric values matter for compatibility.

Dependencies/integration: included by RADOS metadata and sync code.

Risks and test signals: adding/reordering enum values can corrupt interpretation of persisted mdlog records. Encoding tests should validate string dump/decode mappings in `rgw_metadata.cc`.
