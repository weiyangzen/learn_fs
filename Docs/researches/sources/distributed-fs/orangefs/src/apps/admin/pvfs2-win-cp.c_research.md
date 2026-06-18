<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-win-cp.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-win-cp.c

**Purpose:** `pvfs2-win-cp` is the Windows copy utility for copying between Windows files and OrangeFS files, preserving selected permissions and supporting datafile count/stripe-size creation hints.

**Important APIs, types, and functions:** `file_object` abstracts `WIN_FILE` and `PVFS2_FILE`. `init_credential()` creates a root-like credential with issuer `C:<hostname>`. `resolve_filename()` checks the Windows stat tab arrays for mount prefixes. `generic_open()` handles source lookup/open and destination create, using `PVFS_sys_lookup`, `PINT_lookup_parent`, `PVFS_sys_ref_lookup`, `PVFS_sys_dist_lookup`, `PVFS_sys_dist_setparam`, and `PVFS_sys_create`. `generic_read()`/`generic_write()` wrap `fread`/`fwrite` or `PVFS_sys_read`/`PVFS_sys_write`. `generic_cleanup()` preserves permissions via `_chmod` or `PVFS_sys_setattr`.

**Control flow:** The parser handles `-s`, `-n`, `-b`, `-t`, `-v` manually with Windows case-insensitive comparisons. `main()` initializes PVFS, resolves source/destination, creates credentials, opens both ends, copies in a loop until read returns zero, optionally prints throughput, cleans up, finalizes, and frees hints.

**State and persistence:** It reads and writes file data, creates destination files, and updates destination attributes. PVFS destinations are created with broad permissions then adjusted in cleanup; a crash before cleanup can leave permissive files.

**Dependencies and integration points:** It depends on Windows headers/runtime, OrangeFS Windows stat tab globals, PVFS hints from environment, sysint I/O, and path conversion helpers.

**Risks and edge cases:** `init_credential()` fabricates userid 0, which is security-sensitive. Destination overwrite is refused for PVFS but Windows `fopen(...,"w")` truncates. Text-mode `fopen("r"/"w")` can corrupt binary data on Windows. `PVFS_Request_free` is skipped on read/write error. Tests should cover all copy directions, binary data, existing targets, directory destinations, stripe/datafile options, permission preservation, and failure before cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-win-cp.c -->
