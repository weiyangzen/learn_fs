# sources/distributed-fs/orangefs/src/apps/devel/pvfs2-remove-prealloc.c

## Purpose
`pvfs2-remove-prealloc.c` is a development utility for inspecting, and optionally deleting, preallocated handle pool records from a server's DBPF key/value database. It is meant for storage repair or cleanup scenarios where a specific server host has precreated handle pool entries that should be removed from `keyval.db`, using pool handles discovered from `collection_attributes.db`.

## Important APIs, Types, and Functions
`options_t` carries `remove`, `dbpath`, `hexdir`, and `host`. `main()` parses options, opens `collection_attributes.db` and `keyval.db`, then calls `find_pool_keys()`. `find_pool_keys()` iterates PVFS dataspace type values by powers of two, constructs keys of the form `precreate-pool-<host>-<type>`, performs `DBPF_DB_CURSOR_SET` lookups in the collection attribute DB, and passes the resulting pool handle to `remove_preallocated_handles()`.

`remove_preallocated_handles()` opens a write cursor on `keyval.db`, seeks to the count record keyed by the pool handle, prints it via `print_keyval()`, and optionally deletes it with `dbpf_db_cursor_del()`. It then walks following records while they match the same pool handle with `key.len == 16` and `val.len == 0`, printing and optionally deleting each preallocated handle record. `print_keyval()` is a defensive-ish formatter for DBPF key/value records; it recognizes handle lists (`dh`/`de`), distribution names (`md`), filename-to-handle records, and count-style records.

## Control Flow
The utility defaults to dry-run mode. `--remove` enables destructive deletion; otherwise it prints every record it would remove. Required inputs are `--dbpath`, `--hexdir`, and intended `--host`. After both DBs open, the program searches pool keys for each dataspace type until `PVFS_TYPE_INTERNAL` is reached. Any failed pool-key lookup currently aborts the whole scan rather than continuing to the next type.

## State and Persistence
Persistent state is the DBPF storage space. In dry-run mode it should only read. In remove mode it mutates `keyval.db` by deleting the preallocated count record and zero-length handle records for each discovered pool. No backup, transaction wrapper, or recovery marker is created by this tool. In-memory state consists of cursor buffers, a stack `dbpf_keyval_db_entry`, and global parsed options.

## Dependencies and Integration Points
The file uses the same DBPF and PVFS internal storage headers as `pvfs2-db-display.c`, plus record layout knowledge for precreate pool naming and `struct dbpf_keyval_db_entry`. It is operationally coupled to server host string formatting: the host passed with `--host` must match the stored precreate-pool key exactly.

## Risks and Edge Cases
The `--host` validation is ineffective: `opts.host` is a fixed array, so `if (! opts.host)` can never detect a missing option. The correct check would mirror `dbpath`/`hexdir` and compare against an empty string. `find_pool_keys()` leaks the allocated `key_string` on every iteration and returns the prior `ret` value on allocation failure. It does not close `dbc_p` on early return paths. Cursor values are decoded with raw casts and little length validation. In remove mode, interruption after partial deletion can leave a pool partially cleaned. Failed lookup for one type prevents scanning later types, which may be too strict if not every type has a precreate pool.

## Test Signals
Fixture tests should build small DBPF databases containing collection attributes for multiple `precreate-pool-<host>-<type>` keys and corresponding keyval count/handle records. Verify dry-run output is stable and remove mode deletes only matching pool records. Include missing-host argument tests to expose the current validation bug, missing pool type tests, malformed count/value sizes, and interruption/retry behavior. A post-run DB dump with `pvfs2-db-display.c` is a useful integration signal.
