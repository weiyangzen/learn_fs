<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-viewdist.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-viewdist.c

**Purpose:** `pvfs2-viewdist` displays a file or directory distribution by reading OrangeFS extended attributes for the distribution descriptor and datafile handles, then mapping handles to server names.

**Important APIs, types, and functions:** `file_object` abstracts Unix and PVFS2 targets. `generic_dist()` reads `system.pvfs2.<METAFILE_DIST_KEYSTR>` via `fgetxattr` or `PVFS_sys_geteattr`. `generic_server_location()` reads `system.pvfs2.<DATAFILE_HANDLES_KEYSTR>` and uses `PINT_cached_config_get_server_name`. `generic_open()` resolves and validates the target. `main()` decodes the distribution with `PINT_dist_decode` and prints `dist->methods->params_string`.

**Control flow:** The tool requires `-f`. It initializes PVFS, resolves the file as PVFS2 or local, opens/looks up attributes, reads distribution and datafile handle xattrs, decodes and prints distribution name/parameters, maps the metadata handle to a server, and prints each datafile server/handle.

**State and persistence:** It is read-only but allocates buffers for xattr data and distribution decoding. It observes persisted xattrs and cached server config.

**Dependencies and integration points:** It depends on xattr support, PVFS sysint, PINT distribution implementations (`basic`, `simple_stripe`, `varstrip`), cached config, and serialized distribution format.

**Risks and edge cases:** The fixed 4096-byte xattr buffers can be too small for large datafile lists or distribution descriptors. The metadata-server mapping assumes a PVFS2 object even after Unix-file fallback, using `src.u.pvfs2` fields. Some error paths leak `dist_buf` or server buffers. Tests should cover PVFS files with each distribution type, local mounted xattrs, many datafiles >4096 bytes, directories, missing xattrs, and metadata server mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-viewdist.c -->
