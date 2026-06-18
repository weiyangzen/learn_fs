# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_device.c

## Purpose

`uverbs_std_types_device.c` defines global device-scope ioctl methods: context allocation/query, invocation of legacy write commands through ioctl marshalling, object handle enumeration, port queries, port speed query, GID table query, and single GID entry query. It is the bridge between the device object in the ioctl UAPI and device/context metadata needed by userspace.

## Important APIs, Types, and Functions

- `UVERBS_METHOD_INVOKE_WRITE` lets ioctl users invoke legacy `write`/`write_ex` commands by command number using ioctl attributes for core and provider buffers.
- `gather_objects_handle()` and `UVERBS_METHOD_INFO_HANDLES` enumerate live uobject handles of a requested object type for the current uverbs file.
- `copy_port_attr_to_resp()` maps `ib_port_attr` into the legacy/extended query-port response, including GRH-required, OPA LID conversion, link layer, and speed fields.
- `UVERBS_METHOD_QUERY_PORT`, `UVERBS_METHOD_QUERY_PORT_SPEED`, `UVERBS_METHOD_GET_CONTEXT`, and `UVERBS_METHOD_QUERY_CONTEXT` expose device and ucontext metadata.
- `copy_gid_entries_to_user()`, `UVERBS_METHOD_QUERY_GID_TABLE`, and `UVERBS_METHOD_QUERY_GID_ENTRY` expose cached GID information with variable-sized userspace entry support.
- `DECLARE_UVERBS_GLOBAL_METHODS(UVERBS_OBJECT_DEVICE, ...)` attaches these methods to the global device object.

## Control Flow

`GET_CONTEXT` checks that the device is not disassociated, writes number of completion vectors and core-support flags, allocates a ucontext, and initializes it. `QUERY_CONTEXT` requires an existing ucontext and delegates provider-specific context query. Port and GID queries first retrieve the ucontext, validate ports/flags/sizes, call RDMA core query helpers or provider speed op, and copy extensible responses with zero-fill behavior.

`INVOKE_WRITE` resolves a legacy command in `uapi->write_methods`, fills `attrs->ucore` and driver `ib_udata` from ioctl pointer attributes, checks minimum core request/response sizes, calls the legacy handler, and finalizes any NEW uobject set by the handler.

## State and Persistence Behavior

`GET_CONTEXT` creates persistent per-file ucontext state; query methods only read device/cache state. `INFO_HANDLES` snapshots the file's uobject list under `uobjects_lock` into bundle memory. GID queries acquire and release `gid_attr` references and use RCU around optional netdev lookup.

## Dependencies and Integration Points

The file depends on `ib_uverbs_get_ucontext()`, `ib_alloc_ucontext()`, `ib_init_ucontext()`, `uapi_get_method()`, RDMA cache helpers (`rdma_query_gid_table`, `rdma_get_gid_attr`), port helpers (`ib_query_port`, `rdma_is_port_valid`, `rdma_port_get_link_layer`), and provider ops such as `query_ucontext` and `query_port_speed`. It is chained into the core API by `uverbs_uapi.c`.

## Risks and Edge Cases

Key risks include creating multiple contexts on one file, invoking legacy handlers with mismatched core/provider buffer lengths, returning variable-sized GID entries safely, and enumerating handles while objects are changing. The code uses locks, size checks, optional attribute support, and copy-to-struct-or-zero to reduce compatibility risk. Query-port active speed is capped in the legacy field and also returned in extended form.

## Test Signals

Test GET_CONTEXT once and repeated, disassociation during GET_CONTEXT, legacy write invocation through ioctl, handle enumeration under concurrent create/destroy, query-port on invalid ports, provider missing speed/query ops, GID table with smaller/larger entry sizes, GID entry with missing netdev, and core-support flag contents.
