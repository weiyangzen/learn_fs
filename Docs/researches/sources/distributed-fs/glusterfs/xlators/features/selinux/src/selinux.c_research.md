# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.c

## Purpose
`selinux.c` implements a GlusterFS feature translator that remaps the public SELinux xattr name `security.selinux` to Gluster's internal trusted xattr `trusted.glusterfs.selinux` while requests pass through the translator stack.

## Important APIs, types, and functions
The FOP table provides `getxattr`, `fgetxattr`, `setxattr`, and `fsetxattr`. `selinux_getxattr()` and `selinux_fgetxattr()` rewrite requested name `SELINUX_XATTR` to `SELINUX_GLUSTER_XATTR` when enabled, wind to the child, then their callbacks rename the returned dictionary key back to `security.selinux`. `selinux_setxattr()` and `selinux_fsetxattr()` rename dictionary keys from public to internal form before forwarding. `selinux_priv_t` stores only `selinux_enabled`.

## Control flow
Each FOP validates `this->private`, performs name/dictionary rewriting when enabled, winds the request to `FIRST_CHILD(this)`, and strict-unwinds in the callback. A NULL xattr name is treated as listxattr-style input and forwarded without rewriting. `init()` requires exactly one child, warns on no parents, allocates private state, reads the `selinux` option, creates a local pool, and stores `this->private`. `reconfigure()` reloads the option, `fini()` frees private state and destroys the pool, and `mem_acct_init()` registers memory types.

## State and persistence behavior
The translator keeps only in-memory configuration in `selinux_priv_t`; it does not persist state itself. Persistence impact is indirect: on setxattr/fsetxattr it changes which backend xattr key is stored.

## Dependencies and integration points
The file depends on GlusterFS xlator APIs, dictionaries, stack macros, option parsing, memory accounting, and message IDs. It integrates through `xlator_api` with identifier `selinux`, category `GF_MAINTAINED`, and the settable `selinux` boolean option defaulting to on.

## Risks and edge cases
Both setxattr paths use `if (!priv->selinux_enabled && !dict) goto off;`; this means a disabled translator with a non-NULL dict still attempts to rename keys, likely contrary to the intended "disabled means pass through" behavior. If `dict` is NULL while enabled, `dict_rename_key()` may be called with NULL unless the dictionary API tolerates it. Rewriting mutates caller dictionaries in place before forwarding, which can affect later translators if they expect the original key. Error paths return `EINVAL` for validation and dictionary failures rather than preserving richer causes.

## Test signals
Tests should cover enabled and disabled get/set/fget/fset flows, NULL names for listxattr, dictionaries with and without `security.selinux`, missing internal xattr on get, and reconfigure toggling. A regression test should assert disabled mode leaves xattr names unchanged for non-NULL dictionaries.
