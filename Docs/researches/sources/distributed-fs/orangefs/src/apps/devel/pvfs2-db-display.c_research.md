# sources/distributed-fs/orangefs/src/apps/devel/pvfs2-db-display.c

## Purpose
`pvfs2-db-display.c` is a development/debugging utility that opens an OrangeFS/PVFS server storage space and prints selected DBPF/Berkeley DB tables in a textual form. It targets the collection-level databases (`collections.db`, `storage_attributes.db`) and the per-collection hex directory databases (`dataspace_attributes.db`, `keyval.db`, `collection_attributes.db`). The output is intentionally low-level: handles, DB keys, dataspace attributes, key/value records, and collection attributes are decoded directly from stored binary records.

## Important APIs, Types, and Functions
The utility is organized around `options_t`, global `opts`, and global `hex`. `main()` parses `--dbpath`, `--hexdir`, and `--hexhandles`, builds each DB path, opens it with `dbpf_db_open()`, and passes the handle to `iterate_database()`. `iterate_database()` creates a DBPF cursor with `dbpf_db_cursor()`, repeatedly calls `dbpf_db_cursor_get(..., DBPF_DB_CURSOR_NEXT, ...)`, and dispatches every key/value pair to one of the typed print callbacks.

The print callbacks are the substantive decoders. `print_collection()` and `print_storage()` treat values as `int32_t`. `print_dspace()` interprets values as `struct PVFS_ds_attributes_s`, formats ctime/mtime/atime, calls `print_ds_type()`, and emits union fields for metafiles, datafiles, and dirdata. `print_keyval()` decodes `struct dbpf_keyval_db_entry`, recognizes directory entries, named attributes such as `dh`, `md`, `st`, `ml`, `nd`, distributed-directory keys (`/dda`, `/ddh`, `/ddb`), xattrs under `user.`, and count records. `print_collection_attr()` prints 8-byte attributes as handles/integers and other attributes as strings.

## Control Flow
Argument validation is mandatory for `--dbpath` and `--hexdir`; help exits immediately. Once arguments pass, `main()` allocates a reusable path buffer sized for the longest known DB name, tries to open each database in a fixed order, prints a header only for databases that open successfully, iterates the records, then closes the DB. Missing or unopenable DBs are silently skipped rather than treated as fatal after argument parsing. Cursor iteration stops normally on `TROVE_ENOENT`; any other cursor status is reported.

## State and Persistence
The program is read-only at the DBPF layer. Persistent state lives entirely in the server storage databases passed by path. In-memory state is minimal: `opts`, `hex`, the reusable path buffer, cursor key/value buffers, and temporary decoded time strings. There is no caching, no config file, and no output persistence beyond stdout/stderr.

## Dependencies and Integration Points
The file depends on OrangeFS/PVFS internal headers (`pvfs2-types.h`, `trove-types.h`, `pvfs2-storage.h`, `pvfs2-internal.h`, `trove-dbpf/dbpf.h`, `pint-util.h`) and the DBPF storage API. It is tied to on-disk record layouts and constants such as `DBPF_DB_COMPARE_DS_ATTR`, `DBPF_DB_COMPARE_KEYVAL`, `DBPF_DIRECTORY_ENTRY_TYPE`, `PVFS_TYPE_*`, and `PVFS_SYS_LAYOUT_*`. It integrates as a developer application, not as part of the server runtime.

## Risks and Edge Cases
The path buffer clearing uses `memset(path, path_len, sizeof(char))`, which only clears one byte and writes `path_len` into it; subsequent `sprintf()` overwrites enough bytes for current usage but the pattern is wrong. `iterate_database()` leaks `key.data` and `val.data`, and if only one allocation succeeds it returns without freeing or closing the cursor. Many decoders cast raw bytes to structs or integer pointers without validating `key.len`/`val.len`, so malformed or version-skewed DB contents can trigger out-of-bounds reads or alignment faults. `print_keyval()` mutates unterminated xattr values by writing a NUL into the DB cursor buffer. The tool assumes native endianness and matching OrangeFS structure layouts.

## Test Signals
Useful validation is mostly fixture-driven: run against a known storage space with collections, files, directories, symlinks, xattrs, distributed directories, and multiple dataspace types, then compare output to expected decoded records. Negative tests should include missing DB files, too-small values for recognized keys, invalid `/dda` lengths, and binary `user.*` xattrs. Memory tooling should flag the cursor buffer leak and error-path leaks. Regression tests should cover `--hexhandles` output and the mtime conversion through `PINT_util_mkversion_time()`.
