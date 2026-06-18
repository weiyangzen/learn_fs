# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-linkfile.c

## Purpose

`dht-linkfile.c` creates, validates, resolves, and attribute-heals DHT linkfiles. Linkfiles are special regular files with `DHT_LINKFILE_MODE` plus a linkto xattr that point from a hashed location to the actual cached/target subvolume, allowing lookup and migration flows to find data that is not on the hash-selected child.

## Important APIs, Types, and Functions

`dht_linkfile_create` is the exported creation helper. It stores the caller's callback, copies the target loc, prepares gfid/internal/linkto xattrs, creates the special file as root, and winds a child `create`. `dht_linkfile_create_cbk` marks success, handles `EEXIST` by looking up the existing file with a linkto xattr request, and then dispatches the original callback. `dht_linkfile_lookup_cbk` verifies that the existing object really is a DHT linkfile. `dht_linkfile_subvol` reads the configured linkto xattr and maps the stored subvolume name to a child xlator. `dht_linkfile_attr_heal` asynchronously sets UID/GID on a newly created root-owned linkfile, using `dht_linkfile_setattr_cbk` for cleanup.

## Control Flow

Creation uses `local->params` when present or a temporary dict otherwise. It optionally sets `gfid-req`, always marks the FOP internal, stores `conf->link_xattr_name = tovol->name`, creates an fd when the caller did not provide one, and winds `create` to `fromvol` with `S_IFREG | DHT_LINKFILE_MODE`. On `EEXIST`, it sends `lookup` to confirm linkfile semantics and preserve race tolerance. Attribute heal copies the final file GFID into `local->loc`, copies the frame/local, marks the setattr internal, temporarily uses superuser credentials, and sets only UID/GID on `local->link_subvol`.

## State and Persistence Behavior

The linkfile itself is persistent child filesystem state. Its key persistent marker is the trusted DHT linkto xattr named by `conf->link_xattr_name`, whose value is a subvolume name. Creation may persist a requested GFID. Runtime state is in `local->linkfile`, `local->linked`, `local->link_subvol`, `local->fd`, and the copied frame used for async attr heal.

## Dependencies and Integration Points

This file depends on DHT config xattr names, `check_is_linkfile`, child `create`, `lookup`, and `setattr` FOPs, frame superuser helpers, dict APIs, and `DHT_MARK_FOP_INTERNAL`. It integrates with create, rename, hardlink, lookup, and rebalance paths that need linkto forwarding and with helper migration checks that resolve linkto xattrs through `dht_linkfile_subvol`.

## Risks and Test Signals

Risks include races on `EEXIST`, mismatched or stale linkto subvolume names, failure to heal root-owned UID/GID, leaking the temporary fd/dict on error, creating with the wrong GFID, and treating a normal file with linkfile mode or xattr inconsistently. Tests should cover successful linkfile creation, existing linkfile lookup validation, existing non-linkfile warning path, missing/unknown linkto target, gfid-req propagation, internal-FOP xattr presence, attr-heal success/failure, root credential use, and lookup/migration resolution from linkto xattr to child xlator.
