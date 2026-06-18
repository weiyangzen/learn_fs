# sources/distributed-fs/ceph-client/fs/overlayfs/params.h

## Purpose
`params.h` is the small shared interface between OverlayFS mount parsing and superblock setup. It declares parser tables, the fs-context data structures, and the option verification/display/free entry points used by `params.c`, `super.c`, and the filesystem type registration.

## Important APIs, types, and functions
`struct ovl_opt_set` records whether the user explicitly requested `metacopy`, `redirect`, `nfs_export`, or `index`; this matters because `ovl_fs_params_verify()` distinguishes explicit conflicts from defaults that can be adjusted. `OVL_MAX_STACK` caps lower layers at 500. `struct ovl_fs_context_layer` stores one user-provided layer name plus its resolved `struct path`. `struct ovl_fs_context` stores upper/work paths, dynamic lower capacity/counts, count of data-only layers, explicit-option set, the lower array, preserved legacy `lowerdir=` string, and casefold consistency state.

The file declares `ovl_parameter_spec[]`, `ovl_parameter_redirect_dir[]`, `ovl_init_fs_context()`, `ovl_free_fs()`, `ovl_fs_params_verify()`, `ovl_show_options()`, and `ovl_xino_mode()`.

## Control flow
During `fsopen()`/mount setup, `ovl_init_fs_context()` allocates and attaches `struct ovl_fs_context` to `fc->fs_private`. `params.c` mutates this context while parsing mount options. `super.c` consumes it during `ovl_fill_super()`, transferring lowerdir strings and path references into `struct ovl_fs` layers. On failure or context release, `ovl_free()` calls the context free helper and `ovl_free_fs()`.

## State and persistence
The context is temporary mount-construction state, not persistent state. It preserves user-visible mount strings for later `show_options` and owns path references until superblock setup clones mounts or drops the context. `casefold_set` and the mount-private `ofs->casefold` jointly ensure all layer directories are consistently casefolded or not.

## Dependencies and integration points
It depends on `linux/fs_context.h` and `linux/fs_parser.h`, and forward declares `struct ovl_fs` and `struct ovl_config` to avoid pulling all OverlayFS internals into users. `super.c` relies on the lower ordering contract: regular lower layers first, data-only lower layers last, and `nr` includes `nr_data`.

## Risks
Changing `OVL_MAX_STACK`, lower ordering fields, or explicit-option tracking affects mount validation and feature downgrade behavior. Incorrect ownership expectations for `lowerdir_all`, layer `name`, or `path` can cause leaks, double frees, or wrong `/proc/mounts` output.

## Test signals
Compile-time coverage should catch prototype drift. Runtime signals include correct handling of legacy and new lower options, data-layer counts, explicit conflict diagnostics, casefold validation, and cleanup after parse failures.
