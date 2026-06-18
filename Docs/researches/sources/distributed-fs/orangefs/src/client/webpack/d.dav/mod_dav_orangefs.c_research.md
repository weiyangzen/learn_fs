# sources/distributed-fs/orangefs/src/client/webpack/d.dav/mod_dav_orangefs.c

## Purpose
This file implements an Apache `mod_dav` repository provider backed by OrangeFS/PVFS. It maps WebDAV resources, live properties, dead properties, file I/O, collections, COPY/MOVE/DELETE, locks, and optional Basic authentication onto OrangeFS objects, credentials, and extended attributes.

## Important APIs, Types, and Functions
- Apache/mod_dav integration uses `dav_provider`, `dav_hooks_repository`, `dav_hooks_propdb`, `dav_hooks_liveprop`, `dav_hooks_locks`, `dav_resource`, `dav_stream`, `dav_db`, `dav_lockdb`, `dav_lock`, `dav_walk_params`, `dav_response`, `dav_register_provider`, `dav_register_liveprop_group`, and `dav_hook_*`.
- Apache auth integration registers an `authn_provider` named `this_module` that authenticates with PAM.
- OrangeFS/PVFS integration uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential`, `PVFS_sys_lookup`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, `PVFS_sys_readdir`, `PVFS_sys_read`, `PVFS_sys_write`, `PVFS_sys_create`, `PVFS_sys_mkdir`, `PVFS_sys_remove`, `PVFS_sys_rename`, `PVFS_sys_geteattr`, `PVFS_sys_seteattr`, `PVFS_sys_deleattr`, and `PVFS_sys_listeattr`.
- `dav_orangefs_server_conf` stores `PVFSInit`, default uid/gid/perms, and cert path.
- `dav_orangefs_dir_conf` stores PUT and READ buffer sizes.
- `dav_resource_private` stores OrangeFS refs, parent refs, credentials, permission attributes, URI/path pieces, walk flags, and lock-null state.
- `dav_stream` buffers PUT writes and tracks OrangeFS offsets.
- `dav_db` carries dead-property lookup context and namespace prefix mapping.
- Helper functions `orangeAttrs()`, `getStatAttrs()`, `orangeRead()`, `orangeWrite()`, `orangeRemove()`, `orangeMkdir()`, `orangeCopy()`, `orangePropCopy()`, `orangeCreate()`, `credInit()`, and `credCopy()` form the low-level OrangeFS adapter.

## Control Flow
1. `register_hooks()` registers the optional auth provider, post-config init hook, live-property hooks, live-property group, and DAV provider named by `PROVIDER_NAME`.
2. `dav_orangefs_init_handler()` optionally runs `PVFS_util_init_defaults()` based on `PVFSInit` and adds the build `VERSION`.
3. `dav_orangefs_get_resource()` creates a `dav_resource`, initializes default permissions, strips a trailing slash for lookup, calls `orangeAttrs("stat")`, maps OrangeFS file type to DAV flags, redirects directory URIs lacking a trailing slash, and handles lock-null PUT setup.
4. Parent lookup, resource equality, stream open/write/close, GET delivery, MKCOL, COPY, MOVE, DELETE, and recursive walks are implemented through the repository hook table.
5. PUT uses fixed-size buffers and writes full buffers immediately through `orangeWrite()`; final partial data is flushed in `close_stream()`.
6. GET on directories serves `index.html` when present or emits an HTML directory listing from `PVFS_sys_readdir`; GET on files streams repeated `orangeRead()` calls.
7. COPY recurses through `dav_orangefs_walk()` and copies dead properties; MOVE uses `PVFS_sys_rename()`.
8. DELETE recurses through children first, then removes the now-empty directory or file with `PVFS_sys_remove()`.

## Property, Lock, and Credential Behavior
- Dead properties are stored as OrangeFS xattrs with key prefix `user.pvfs2.` and names encoded as `localName` or `localName namespaceURI`.
- Reserved xattrs `orangefs_lock` and `orangefs_locknull` store lock and lock-null state.
- Live properties cover `creationdate`, `getcontentlength`, `getetag`, `getlastmodified`, and `getcontenttype`; content length triggers a stat including size.
- PROPPATCH rollback stores the old xattr value or records that a property was new, then restores/removes it on rollback.
- Only exclusive write locks are advertised; shared locks are rejected.
- The optional auth provider uses PAM service `httpd`, a global password buffer, and `auth_conv()`.
- OrangeFS credentials are built from an existing credential, local passwd lookup, LDAP-style uid/gid subprocess environment values, or configured nobody/default uid/gid. `DAVpvfsCertPath` supplies cert/key paths for `PVFS_util_gen_credential()`.

## State and Persistence Behavior
- File and directory content persists as native OrangeFS objects.
- Dead properties, lock state, and lock-null markers persist as OrangeFS extended attributes.
- Runtime refs, credentials, buffer state, path parts, and namespace maps are APR-pool scoped.
- Server config stores PVFS initialization choice, default uid/gid/perms, and certificate path. Directory config stores buffer sizes.
- Debug logging is toggled by `/etc/orangeFSdebugTrigger`; `debug_orangefs` is global.
- OrangeFS name-cache invalidation is used as a one-shot retry strategy for stale refs during concurrent filesystem changes.

## Dependencies and Integration Points
- Requires Apache HTTPD, APR, mod_dav, mod_auth, PAM, and OrangeFS/PVFS client libraries.
- Integrates with `mod_dir` expectations by implementing directory trailing-slash redirects and `index.html` lookahead.
- Uses cert/key files produced by the OrangeFS authn module when `DAVpvfsCertPath` is configured.
- The Makefile embeds `PROVIDER_NAME`, which determines the DAV provider registration name.

## Risks and Edge Cases
- `dav_orangefs_seek_stream()` is explicitly unimplemented but returns success.
- `dav_orangefs_propdb_exists()` always returns 0, `dav_orangefs_find_lock()` is empty, and `dav_orangefs_remove_locknull_state()` has no explicit return value.
- PVFS-to-HTTP error mapping is inconsistent and often generic.
- Fixed-size buffers and unsafe string functions create truncation/overflow risk for long usernames, paths, property names, lock owners, and values.
- PAM handling is not thread-safe due to global `pass[100]` and allocates only one response regardless of `num_msg`.
- Lock storage supports only one serialized lock per resource and only exclusive locks.
- Directory listings write raw names into HTML without escaping.
- Permission checks are hand-rolled from OrangeFS mode bits and may not cover all destination-parent cases.
- Debug logging can expose credentials, paths, lock owners, and property values.

## Test Signals
- Run WebDAV interoperability tests for PROPFIND, PROPPATCH, GET, PUT, MKCOL, COPY, MOVE, DELETE, LOCK, UNLOCK, and lock refresh.
- Add concurrency tests for stale refs during stat, walk, mkdir, copy, and property access.
- Test namespaced properties, XML-valued properties, reserved property rejection, rollback, property copy, and enumeration.
- Test direct locks, indirect locks, expired locks, refresh, lock-null PUT conversion, lock-null UNLOCK removal, shared-lock rejection, and malformed lock xattrs.
- Test PAM success/failure, long passwords, multiple PAM messages, local and LDAP credential mapping, fallback credentials, and cert-path credential generation.
- Test PUT sizes below/equal/above `PutBufSize` and GET/COPY sizes above `ReadBufSize`.
