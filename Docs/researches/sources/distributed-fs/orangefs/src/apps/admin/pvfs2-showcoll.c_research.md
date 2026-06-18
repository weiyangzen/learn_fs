<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-showcoll.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-showcoll.c

**Purpose:** `pvfs2-showcoll` directly inspects TROVE/DBPF storage spaces and collections, listing collections, dataspaces, and optional key/value contents. It is a low-level offline/diagnostic storage viewer.

**Important APIs, types, and functions:** Global paths default to `/tmp/pvfs2-test-space`. `parse_args()` accepts data path, meta path, collection, dspace handle, verbose, and keyval printing. `main()` calls `trove_initialize`, `trove_collection_lookup`, `trove_open_context`, `trove_collection_geteattr` for `ROOT_HANDLE_KEYSTR`, and dispatches to `print_collections`, `print_dspaces`, or `print_dspace`. Key helpers use `trove_dspace_iterate_handles`, `trove_dspace_getattr`, `trove_keyval_iterate`, and format PVFS object attributes, datafile handles, dirents, mirror keys, and meta hints.

**Control flow:** With no collection it iterates up to 32 collections and exits. With a collection it resolves the collection id, opens a TROVE context, fetches the root handle if present, prints collection metadata, then either prints one dspace or iterates all dspaces in batches of 64. If `-k` is set it iterates keyvals one at a time with fixed key/value buffers.

**State and persistence:** This utility is read-only with respect to TROVE data. It opens local storage directly rather than going through PVFS servers, so it observes on-disk DBPF state and can race with active servers.

**Dependencies and integration points:** It depends on TROVE DBPF internals, PVFS object attribute formats, root-handle key strings, and layout of known key names. It is tightly coupled to OrangeFS storage backend structures.

**Risks and edge cases:** Fixed 256/65536 keyval buffers can truncate or fail on larger values. There are memory leaks on some keyval error paths. `print_keyval_pair()` appears to null-terminate `key_p` instead of `val_p` in the printable-value branch. Direct inspection of live storage can produce inconsistent snapshots. Tests should use fixture DBPF collections with known metadata, dirdata, mirror keys, missing root handle, single dspace lookup, and oversized keyvals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-showcoll.c -->
