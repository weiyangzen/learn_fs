# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Attr.inc

## Purpose

`Attr.inc` implements EOS namespace extended-attribute listing, reading, setting, removing, space-attribute merging, and common attribute helper templates. It is the backing implementation for both command-level attribute operations and the XRootD FAttr adapter.

## Important APIs, Types, and Functions

- `attr_ls()` / `_attr_ls()` list attributes for files or directories and hide `eos::kAttrObfuscateKey`.
- `attr_get()` / `_attr_get()` fetch one attribute from path, file metadata, container metadata, or `FileOrContainerMD`, with optional base64 output encoding.
- `attr_set()` / `_attr_set(path,...)` validate input, decode base64 values, validate/convert ACL values, lock metadata for writes, delegate to `_attr_set(item,...)`, and audit changes.
- `_attr_set(FileOrContainerMD&,...)` enforces owner/ACL xattr update rules, exclusive set, application-lock conflicts, ctime updates, store updates, and FUSE refresh registration.
- `attr_rem()` / `_attr_rem()` remove attributes with owner/ACL checks, store updates, FUSE refresh, and audit.
- `mergeSpaceAttributes()`, `listAttributes(...)`, and `getAttribute<T>()` merge configured space attributes into namespace attributes.

## Control Flow

High-level methods map identity with operation-specific access types, perform namespace mapping and external authorization, then call low-level functions. Listing and getting prefetch the item and lock only around metadata reads. Getting always tries to decode base64-stored values and can re-encode when `eos.attr.val.encoding=base64` is present.

Setting validates missing key/value, ignores forced attributes on version directories, decodes `base64:` inputs, validates ACL syntax and numeric id conversion, prefetches the target, captures previous value for audit, write-locks the item, and calls the item-level setter. The item-level setter builds an ACL from existing attrs, rejects unauthorized updates, handles exclusive collision and foreign app-lock collision, updates file/container metadata store, and schedules FUSE refresh after lock release through `FusexCastBatch`.

Removal similarly prefetches, write-locks file or container, enforces owner/ACL permissions, removes the key, updates the backing store, releases the lock before refresh, and audits old/new values.

Space attribute merging reads `mSpaceAttributes` for the selected `sys.forced.space` or `default`, applies special ACL merge operators (`>`, `<`, `|`), optional prefixing, and overwrite/default rules.

## State and Persistence Behavior

Set/remove operations persist changes through `eosView->updateFileStore()` or `updateContainerStore()`, update ctime except for temporary etag keys, emit audit records for xattr and ACL changes, and notify FUSE clients. Space attributes are read from `gOFS->mSpaceAttributes` under `mSpaceAttributesMutex` and are overlaid on reads; they are not written into the target metadata unless explicitly set elsewhere.

## Dependencies and Integration Points

The file depends on `Acl`, `XattrLock`, `SymKey` base64 helpers, `Prefetcher`, metadata locks, `eos::listAttributes`/`eos::getAttribute`, audit helpers, FUSE xcast, MGM stats, token authorization, and external authorization macros. It is used by access checks, find filters, mkdir/chown permission evaluation, FAttr, and command interfaces that expose ACL/attribute management.

## Risks and Edge Cases

- Attribute updates are security-sensitive because ACLs, forced placement, ownership, obfuscation, and app locks are all xattrs.
- Space attribute merging can make reads return values not physically present on the metadata object, so callers must distinguish effective from stored attributes.
- The obfuscate key is intentionally hidden on list/get; tests must prevent leakage.
- ACL value conversion changes user/group names to numeric form; failures must be surfaced as `EINVAL`.
- Removal permission differs for files and containers and token identities are denied on container removal.
- Audit and FUSE refresh happen after metadata updates; failures there are not represented as operation failures in this file.

## Test Signals

Tests should cover list/get/set/remove on files and directories, hidden obfuscation key, base64 input/output, invalid ACL syntax, ACL id conversion failure, owner versus ACL-authorized xattr updates, exclusive set collisions, foreign app-lock `EBUSY`, temp etag ctime exception, audit records for ACL/xattr changes, FUSE refresh emission, version-directory forced-attribute ignore, and space attribute merge operators.
