## sources/distributed-fs/orangefs/src/io/trove/trove-mgmt.c

Purpose: Owns Trove initialization/finalization, method-table selection, storage and collection management wrappers, and context open/close dispatch.

Important APIs and functions: Global method tables map `TROVE_METHOD_DBPF`, `TROVE_METHOD_DBPF_ALTAIO`, `TROVE_METHOD_DBPF_NULLAIO`, and `TROVE_METHOD_DBPF_DIRECTIO` to DBPF management/dspace/keyval/context implementations and variant bstream implementations. `trove_initialize` initializes handle management, installs the method callback, and calls backend initialize. `trove_finalize` shuts down backend and handle management. Storage/collection wrappers include `trove_storage_create/remove`, `trove_collection_create/remove/lookup/iterate/clear`. `trove_open_context` and `trove_close_context` dispatch context operations when initialized.

Control flow: Initialization is guarded by `trove_init_mutex` and `trove_init_status`. With no callback, `TROVE_default_method` returns DBPF for all collections. Backend management operations are normalized so nonnegative returns become `1`, following Trove's immediate-success convention. Collection create selects a method from the new collection ID callback; collection lookup/remove/iterate use an explicit method ID.

State and persistence: Global state includes `global_trove_method_callback`, method tables, `trove_init_status`, and the init mutex. Persistent storage is handled by the selected backend; this file only routes requests.

Dependencies and integration points: Integrates DBPF operation tables, alternate/null/direct bstream variants, handle-management initialization/finalization, `gossip`, and `gen-locks`. Public API declarations live in `trove.h`; vtable contracts live in `trove-internal.h`.

Risks: `trove_initialize` returns while still holding `trove_init_mutex` if Trove is already initialized or if handle-management initialization fails, which can deadlock later calls. Method IDs are used without bounds checks. `trove_finalize` overwrites the backend finalize result with handle-management finalize result, potentially hiding backend errors. Context operations silently return `0` if Trove is not initialized. Repeated initialize/finalize and failed initialization paths need close attention.

Test signals: Test first initialize, duplicate initialize, backend initialization failure, finalize before initialize, finalize after backend failure, all method IDs, null/non-null method callbacks, context open/close before and after initialization, and storage/collection return normalization.
