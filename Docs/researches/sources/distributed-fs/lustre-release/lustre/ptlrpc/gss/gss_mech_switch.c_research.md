# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_mech_switch.c

Purpose: implements the mechanism registry and mechanism-independent GSS operation dispatch layer.

Important APIs/types/functions: `lgss_mech_register()` and `lgss_mech_unregister()` maintain the global `registered_mechs` list under `registered_mechs_lock`. `lgss_name_to_mech()` and `lgss_subflavor_to_mech()` find mechanisms and take module refs. `lgss_mech_get()`/`lgss_mech_put()` manage module ownership. Wrapper functions allocate or validate `gss_ctx` objects and dispatch every operation in `struct gss_api_ops`, including context import/copy/delete, inquire, MIC, wrap/unwrap, bulk prep/wrap/unwrap, and display.

Control flow: mechanisms register at module initialization. Lookup scans the list under spinlock and uses `try_module_get()` to pin a found mechanism. Import allocates a generic `gss_ctx`, pins the mechanism, installs the default hash function, and calls mechanism import. Copy allocates a new generic context, pins the same mechanism, copies hash behavior, and asks the mechanism to duplicate reverse state. Delete calls the mechanism destructor for opaque state, drops the module ref, frees the generic context, and nulls the caller's pointer.

State/persistence: global in-memory registered mechanism list and module refcounts. Contexts are heap objects owned by PTLRPC security contexts.

Dependencies/integration: used by keyring downcall import, service upcall context creation, bulk code, and concrete mechanisms. Depends on module ownership, list/spinlock APIs, `gss_crypto` hash defaults, and `gss_api.h`.

Risks/test signals: duplicate registration is not rejected, unregister assumes the list entry is present, and failed mechanism import after generic allocation depends on caller cleanup via delete. Tests should cover register/unregister ordering, lookup by name/subflavor, module get failures, failed copy cleanup, delete of null/no-context, and wrapper assertions with incomplete ops in debug builds.
