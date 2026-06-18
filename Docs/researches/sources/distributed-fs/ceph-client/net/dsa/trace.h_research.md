# sources/distributed-fs/ceph-client/net/dsa/trace.h

Purpose: defines the DSA tracepoint set for hardware programming of FDB, MDB, LAG FDB, and VLAN operations, including refcount bumps/drops and not-found diagnostics.

Important APIs/types: declares `dsa_db_print()` and `dsa_port_kind()`. Defines `DSA_DB_BUFSIZ`, event classes `dsa_port_addr_op_hw`, `dsa_port_addr_op_refcount`, `dsa_port_addr_del_not_found`, `dsa_vlan_op_hw`, and `dsa_vlan_op_refcount`, plus concrete events such as `dsa_fdb_add_hw`, `dsa_mdb_del_drop`, `dsa_lag_fdb_add_hw`, `dsa_vlan_add_bump`, and `dsa_vlan_del_not_found`.

Control flow: DSA code invokes trace events around switchdev programming. The trace macros capture device name, port kind/index, MAC address, VID, database string, errors, VLAN flags, changed state, and refcounts. The bottom overrides `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>` outside the include guard, per kernel tracepoint convention.

State and persistence: tracepoints have no DSA data ownership. Captured data is emitted to runtime tracing buffers when enabled.

Dependencies and integration: includes DSA, switchdev, etherdevice, bridge, refcount, and tracepoint headers. It is consumed through `trace.c` and by DSA FDB/MDB/VLAN programming paths.

Risks and test signals: risks are trace macro signature drift, invalid pointer lifetime during fast assignment, missing fields in print formats, and buffer-size assumptions for database strings. Compile with tracepoints enabled and exercise add/delete/refcount/not-found cases for ports, LAGs, and bridges.
