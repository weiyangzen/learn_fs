# sources/distributed-fs/ceph-client/fs/overlayfs/params.c

## Purpose
`params.c` implements OverlayFS mount option parsing, default option selection, fs-context lifecycle, option compatibility verification, reconfigure handling, option display, and teardown of mount-private state on failed mounts or unmount.

## Important APIs, types, and functions
It exports `ovl_parameter_spec[]`, `ovl_parameter_redirect_dir[]`, `ovl_xino_mode()`, `ovl_init_fs_context()`, `ovl_free_fs()`, `ovl_fs_params_verify()`, and `ovl_show_options()`. Module parameters define defaults for redirect_dir, redirect_always_follow, xino_auto, index, nfs_export, and metacopy. `enum ovl_opt` maps parser tokens to mount features. Constant tables translate string values for bool, uuid, xino, redirect, verity, and fsync modes.

Parsing helpers include `ovl_next_opt()` for escaped comma splitting, `ovl_parse_monolithic()`, `ovl_parse_param_split_lowerdirs()` for single-colon regular lower and double-colon data layers, path lookup helpers `ovl_mount_dir*()`, consistency checks in `ovl_mount_dir_check()`, lower array growth via `ovl_ctx_realloc_lower()`, layer storage in `ovl_add_layer()`, and reset/free helpers.

## Control flow
`ovl_init_fs_context()` allocates `struct ovl_fs_context` and `struct ovl_fs`, initializes default config from module/build options, installs `ovl_context_ops`, and initializes the whiteout mutex. `ovl_parse_param()` rejects new-api reconfigure changes, parses each parameter, and updates config or layer arrays. `lowerdir=` replaces existing lower layers; `lowerdir+`/`datadir+` append file-or-string paths and are rejected after legacy `lowerdir=`. `override_creds` can replace creator credentials only when current is in the fsopen user namespace.

Before superblock fill proceeds, `ovl_fs_params_verify()` resolves feature dependencies: workdir/index without upper are disabled, volatile without upper is ignored, uuid=on without upper becomes uuid=null, metacopy may force redirect_dir=on, nfs_export may force index=on, nfs_export conflicts with metacopy/verity, userxattr disables default redirect/metacopy unless explicitly allowed, and unprivileged trusted-xattr-dependent features are rejected.

## State and persistence
Mount strings are preserved in `config.upperdir`, `config.workdir`, and `config.lowerdirs` for `/proc/mounts`. `ovl_fs_context` temporarily owns resolved `struct path` objects and user strings until `super.c` consumes them. `ovl_free_fs()` releases traps, work/index dirs, in-use locks, layer mounts, anon bdevs, config strings, credentials, and the `ovl_fs`.

## Dependencies and integration points
The file integrates with the new mount API (`fs_context`), VFS path lookup, parser helpers, capability checks, and `ovl_fill_super()` via `get_tree_nodev()`. It depends on `super.c` to probe actual filesystem capabilities after parsing.

## Risks
Option interaction is complex. Regressions may come from accepting inconsistent lower/data ordering, losing escaped path semantics, mishandling user namespace credentials, or silently enabling features that require trusted xattrs. Freeing paths/strings during parse reset must preserve ownership exactly.

## Test signals
Test legacy mount strings, new API `lowerdir+`/`datadir+`, escaped commas/colons, empty lowerdir, too many layers, casefold mismatch, read-only upper rejection, userxattr conflicts, unprivileged mounts, reconfigure behavior, and `/proc/mounts` rendering of defaults versus explicit options.
