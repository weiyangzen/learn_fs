## sources/distributed-fs/orangefs/src/io/trove/trove-internal.h

Purpose: Defines the internal Trove method ABI: the function-pointer tables that concrete storage backends must implement for bstreams, key/value storage, dataspaces, management, and contexts.

Important APIs and types: `struct TROVE_bstream_ops` covers contiguous and list read/write, resize, validate, flush, and cancel. `struct TROVE_keyval_ops` covers single/list read/write/remove, validate, iteration, flush, and handle-info lookup. `struct TROVE_dspace_ops` covers create/list-create, remove/list-remove, handle iteration, verify, getattr/list-getattr, setattr, cancel, and operation testing. `struct TROVE_mgmt_ops` covers storage/collection lifecycle, collection attributes, setinfo/getinfo, clear, and filesystem configuration. `struct TROVE_context_ops` opens and closes operation contexts. The file also declares version helpers and error translation.

Control flow: This header contains no implementation, but `trove.c` dispatches every public operation by selecting a method ID from `global_trove_method_callback` and invoking the corresponding function pointer in these structs. `trove-mgmt.c` populates method tables with DBPF, alt-aio, null-aio, and direct-io variants.

State and persistence: No state is stored here. The structs are ABI-like contracts; state belongs to the backend implementations and the global method tables.

Dependencies and integration points: Includes Trove/PVFS types and is included by Trove public wrappers and DBPF implementation files. `PVFS_hint` parameters expose higher-layer hint propagation to backends.

Risks: The compiler cannot enforce runtime table completeness. A missing or mismatched function pointer will fail at dispatch time. Some public signatures include hints where older internal operations do not, so wrapper/table consistency must be maintained carefully. Method IDs are used as array indexes elsewhere with little bounds checking.

Test signals: Build all method variants with strict warnings, verify every public `trove_*` wrapper has a matching vtable member with compatible signature, and run startup smoke tests for every `TROVE_METHOD_DBPF*` mode.
