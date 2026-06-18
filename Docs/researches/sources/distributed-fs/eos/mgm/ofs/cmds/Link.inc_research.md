# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Link.inc

## Purpose

`Link.inc` implements symbolic link creation and readlink for EOS namespace entries. It provides client-facing and identity-based symlink wrappers, a low-level `_symlink` namespace mutation, and readlink helpers that fetch the stored link target from file metadata.

## Important APIs, Types, and Functions

- `symlink(source_name,target_name,error,client,infoO,infoN,overwrite)` performs identity mapping, path decoding/mapping for both source and target, external authorization, access gates, and delegates to the identity overload.
- `symlink(source_name,target_name,error,vid,infoO,infoN,overwrite)` remaps source, checks write access on the source/link path, and delegates to `_symlink`.
- `_symlink(...)` validates inputs, checks parent existence and destination existence, optionally removes existing source, creates the link with `eosView->createLink()`, updates parent mtime/store, broadcasts FUSE refresh, and audits.
- `readlink(...)` and `_readlink(...)` map identity/path, authorize read, prefetch file metadata, and return `IFileMD::getLink()`.

## Control Flow

Client-facing symlink decodes `#space#` unless `eos.encodepath` is present, maps both names through namespace mapping, authorizes create on the source path, applies write access gates, and calls the lower overload. The identity overload remaps the source path again, checks `_access(source,W_OK)`, and calls `_symlink`.

`_symlink` rejects null names and identical source/target, checks that the source parent directory exists, checks that the source link path does not exist unless overwrite is requested, optionally removes it, then write-locks the namespace, creates the link metadata, updates parent directory mtime and store, releases the lock, sends FUSE refresh, and audits `SYMLINK`.

Readlink is read-only: it authorizes `AOP_Read`, maps the path, prefetches file metadata without symlink dereference, reads the link string, and returns it.

## State and Persistence Behavior

Symlink creation persists a new link metadata entry and parent mtime updates through `eosView`, emits a parent FUSE refresh, and writes an audit record when enabled. Overwrite can remove an existing entry before creating the new link. Readlink does not mutate state.

## Dependencies and Integration Points

Dependencies include namespace mapping, external authorization, `_access`, `_exists`, `_rem`, `eosView->createLink`, namespace locks, FUSE xcast, audit helpers, and XRootD security/error types. It is reachable through direct OFS calls and FSctl command dispatch.

## Risks and Edge Cases

- Naming is easy to misread: `source_name` is the link path and `target_name` is the link target in `_symlink`.
- Overwrite removes the existing source before creating the new link; creation failure after removal can lose the old entry.
- `_symlink` checks parent existence and source existence with `_exists`, which can invoke redirect-capable behavior depending on overload used.
- Permission is checked on the source/link path with `W_OK`, not directly on the target.
- Readlink assumes the path resolves to file metadata with a link payload; non-link files need coverage.

## Test Signals

Tests should cover encoded spaces, namespace mapping for both paths, create authorization, write-access denial, missing parent, existing source with and without overwrite, identical source/target, successful link metadata and parent mtime update, audit, FUSE refresh, readlink for symlink and non-symlink, and overwrite failure recovery.
