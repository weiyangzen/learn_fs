<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_copy.c -->
## sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_copy.c

**Purpose:** `mdb_copy` is the LMDB environment backup tool included under OrangeFS development utilities. It copies an LMDB environment to stdout or a destination path, optionally compacting pages.

**Important APIs, types, and functions:** `main()` parses `-n`, `-c`, and `-V`. It creates an `MDB_env`, opens it read-only with optional `MDB_NOSUBDIR`, and calls `mdb_env_copyfd2` or `mdb_env_copy2` with optional `MDB_CP_COMPACT`. Signal handlers for SIGPIPE/SIGHUP/SIGINT/SIGTERM are installed but only interrupt system calls through empty handlers.

**Control flow:** The tool validates `srcpath [dstpath]`, opens the environment, copies to `MDB_STDOUT` if no destination is provided, prints an action-specific error on failure, closes the env, and returns success/failure.

**State and persistence:** It reads source LMDB pages and writes a backup copy. Compact copy rewrites page layout in the output but does not mutate the source.

**Dependencies and integration points:** It depends on `lmdb.h`, OpenLDAP LMDB semantics, platform stdout handle definitions, and the OrangeFS build option that includes internal LMDB tools.

**Risks and edge cases:** `mdb_env_close(env)` is called even if `mdb_env_create` failed and left `env` uninitialized. Empty signal handlers do not set a flag, so interrupted copies depend on LMDB/write errors. Tests should cover stdout copy, path copy, compact copy, `MDB_NOSUBDIR`, invalid paths, and interrupted output pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_copy.c -->
