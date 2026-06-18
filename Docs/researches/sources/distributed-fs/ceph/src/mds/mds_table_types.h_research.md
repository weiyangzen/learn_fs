<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mds_table_types.h -->
## sources/distributed-fs/ceph/src/mds/mds_table_types.h

`mds_table_types.h` centralizes small enum definitions and printable names for MDS distributed metadata tables and table operations. It currently identifies `TABLE_ANCHOR` and `TABLE_SNAP`, table-server protocol operation codes, and generic table mutation operations.

The inline helpers `get_mdstable_name`, `get_mdstableserver_opname`, and `get_mdstable_opname` map enum integers to stable strings for logs, dumps, and journal replay diagnostics. Invalid values call `ceph_abort()`, intentionally treating unknown table or op codes as fatal programmer/journal corruption errors.

State behavior is indirect but compatibility-sensitive. `journal.cc` stores table ids and operation ids in `ETableServer`, `ETableClient`, and `EMetaBlob::table_tids`; replay switches on these constants and uses the name helpers for logging. Because these values cross journal/network boundaries, changing numeric assignments would break older logs or messages.

Dependencies are minimal: `std::string_view` and `ceph_assert.h` for `ceph_abort`. Integration points include `MDSTableServer`, `MDSTableClient`, `MMDSTableRequest`, journal replay, and any table-specific implementation such as anchor/snap tables.

Risks: adding new tables or ops requires updating all switch helpers and replay logic; abort-on-unknown is useful for corruption detection but harsh for forward compatibility; negative server op values encode reply/client-directed meanings that must match message handling. Test signals include table op encode/decode, journal replay of prepare/commit/rollback/server-update/ack, and logging/dump tests for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mds_table_types.h -->
