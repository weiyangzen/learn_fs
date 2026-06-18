# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkdir.c

Purpose: `pvfs2-mkdir.c` creates one or more OrangeFS directories, with options for mode, parent creation, and distributed-directory sizing hints.

Important APIs, types, and functions: `struct options` stores directory arguments, mode, `init_num_dirdata`, `max_num_dirdata`, `split_size`, verbosity, and parent creation. Key functions are `parse_args`, `make_directory`, `read_mode`, `read_init_num_dirdata`, `read_max_num_dirdata`, `read_split_size`, `enable_verbose`, and `enable_parents`. OrangeFS calls include `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_sys_lookup`, and `PVFS_sys_mkdir`. It uses `PVFS_sys_attr` fields `distr_dir_servers_initial`, `distr_dir_servers_max`, and `distr_dir_split_size`.

Control flow: parsing accepts up to `MAX_NUM_DIRECTORIES`, fills defaults for mode and dirdata controls, and stores argv directory pointers. Main allocates parallel arrays for PVFS-relative paths and fsids, initializes OrangeFS, resolves every requested directory, generates one credential, and calls `make_directory` for each. `make_directory` splits the target PVFS path into parent and basename with `dirname`/`basename`, rejects root, populates directory attributes, looks up the parent, optionally recurses to create missing parents on `-p`, then calls `PVFS_sys_mkdir`.

State and persistence: successful calls persist new directory objects in OrangeFS metadata, including permission bits and distributed-directory hints. No local files are written. The command reads the process umask through `PVFS_util_get_umask` when no mode is supplied.

Dependencies and integration points: it follows sysint admin utility conventions and relies on `libgen` path mutation semantics. It integrates with OrangeFS distributed-directory handling by passing directory data handle counts and split threshold in the mkdir attrs.

Risks: the recursive parent creation path uses `dirname` on multiple mutable buffers and then reuses `parentdir_ptr`; pointer lifetime and mutation order are subtle. Numeric option parsing with `sscanf` only checks parse success, not positivity or semantic constraints between initial and max dirdata. `PVFS_ATTR_SYS_ALL_SETABLE` is used with mostly zeroed attrs, which may unintentionally set fields beyond the intended subset. Some allocation and resolve failures leak earlier allocations or skip finalize. Existing-directory behavior simply reports `PVFS_sys_mkdir` errors rather than matching GNU `mkdir -p` idempotence.

Test signals: create one and many directories, exceed 100 args, mode default with umask, explicit octal mode, invalid mode text, `-p` for missing nested parents, `-p` when target already exists, root path rejection, invalid pvfstab path, permission-denied, `--init-num-dirdata`, `--max-num-dirdata`, and `--split-size` propagation verified through stat/fsck metadata.
