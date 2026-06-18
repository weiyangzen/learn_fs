# sources/distributed-fs/ceph/src/osd/objclass.cc

## Purpose

`objclass.cc` implements the classic OSD-side object class helper ABI. Object class methods receive an opaque `cls_method_context_t`; this file casts it back to `PrimaryLogPG::OpContext **`, builds one or more `OSDOp` records, and dispatches them through `PrimaryLogPG::do_osd_ops()`. It is the bridge that lets dynamically loaded class code read, write, stat, mutate xattrs, manipulate omap, inspect request/cluster metadata, and start class gather operations without knowing `PrimaryLogPG` internals.

## Important APIs and Functions

The C-style helpers include `cls_call`, `cls_getxattr`, `cls_setxattr`, `cls_read`, and `cls_get_request_origin`. The C++ helpers add object lifecycle and IO APIs such as `cls_cxx_create`, `cls_cxx_remove`, `cls_cxx_stat`, `cls_cxx_stat2`, `cls_cxx_read2`, `cls_cxx_write2`, `cls_cxx_write_full`, `cls_cxx_replace`, `cls_cxx_truncate`, and `cls_cxx_write_zero`. Attribute and omap helpers include `cls_cxx_getxattr`, `cls_cxx_getxattrs`, `cls_cxx_setxattr`, `cls_cxx_map_get_all_vals`, `cls_cxx_map_get_keys`, `cls_cxx_map_get_vals`, `cls_cxx_map_read_header`, `cls_cxx_map_get_val`, `cls_cxx_map_get_vals_by_keys`, `cls_cxx_map_set_val`, `cls_cxx_map_set_vals`, `cls_cxx_map_clear`, `cls_cxx_map_write_header`, `cls_cxx_map_remove_range`, and `cls_cxx_map_remove_key`. Cluster/object metadata helpers expose version, subop number, features, OSD release constraints, config, object info, snapset sequence, manifest reference count, allocation size, and pool stripe width. `cls_cxx_chunk_write_and_set` composes a write with a `cas.chunk_set` class call, and `cls_cxx_gather`/`cls_cxx_get_gathered_data` manage multi-object class gather state through `GatherFinisher`. `cls_log` provides object-class logging.

## Control Flow

Most helpers allocate a local `std::vector<OSDOp>`, fill the operation opcode and union fields, encode request payload into `OSDOp::indata`, and invoke `(*pctx)->pg->do_osd_ops(*pctx, ops)`. Return handling is consistent: negative values propagate; successful reads either `malloc` and copy to C buffers or move `bufferlist` output into caller-owned objects. Decoding helpers catch `ceph::buffer::error` and convert malformed OSD replies to `-EIO`. Gather setup stores a finisher in `OpContext::op_finishers` keyed by the current subop number, initializes a result map for all source objects, then asks `PrimaryLogPG::start_cls_gather()` to run the distributed class call.

## State and Persistence Behavior

The file itself owns no durable state. Persistence is delegated to generated OSD operations, so object data, xattrs, omap state, snapshots, rollbacks, and deletes follow normal PG transaction semantics. Temporary state is limited to in-flight `OSDOp` vectors and `GatherFinisher::src_obj_buffs`, which lives in the op context until the relevant suboperation completes. `cls_current_version()` and object info accessors read projected PG/object state from the current operation context rather than querying storage directly.

## Dependencies and Integration Points

This file depends on `objclass/objclass.h` for the exported ABI, `PrimaryLogPG` for execution, `ClassHandler` for logging context, Ceph buffer encoding/decoding, config access, and OSD operation constants. It is reached by dynamically loaded object classes and feeds back into the same OSD op execution path used by clients. The helper functions must stay wire-compatible with method payload encodings expected by `do_osd_ops()` and by omap/xattr/class op handlers.

## Risks and Test Signals

Key risks are ABI drift, incorrect opcode payload layout, missed length validation, malloc ownership mistakes in C helpers, and unexpected side effects from class helpers that compose multiple OSD ops. `cls_get_client_features()` assumes a live connection on the request. Omap helpers rely on decode shape stability. Gather logic asserts finisher insertion and couples tightly to `current_osd_subop_num`. Good test signals include object-class integration tests for read/write/xattr/omap/stat/rollback paths, negative decode tests, class method chaining via `cls_call`, gather completion behavior, and log-level gating for `cls_log`.
