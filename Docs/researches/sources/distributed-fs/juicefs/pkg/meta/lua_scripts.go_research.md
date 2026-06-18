# sources/distributed-fs/juicefs/pkg/meta/lua_scripts.go

## Purpose

`lua_scripts.go` embeds Redis Lua scripts used by the Redis metadata backend for atomic lookup and path resolution. The scripts reduce round trips and preserve consistent Redis-side error behavior for hot namespace operations.

## Important Scripts

`scriptLookup` takes a directory hash key and entry name, fetches the encoded edge with `HGET`, unpacks the inode from bytes after the type byte, rejects inode values above `4503599627370495` because Lua numbers are doubles with 52 significant bits, and returns `{ino, GET("i"..ino)}`. Missing entries raise `ENOENT`; too-large inode values raise `ENOTSUP`.

`scriptResolve` is a fuller path resolver. It defines `unpack_attr` for runtime attr bytes, `get_attr` for `i<ino>` records, `lookup` for directory hash entries, `has_value` for gid membership, `can_access` for execute permission checks, and `resolve` for iterating slash-separated path components. It rejects symlink traversal and too-large inode values with `ENOTSUP`, non-directory traversal with `ENOTDIR`, missing names/attrs with `ENOENT`, and insufficient execute permission with `EACCESS`. It returns `{inode, attr-bytes}` for the final node.

## Control Flow And State

Both scripts operate entirely inside Redis using metadata key conventions: directory entries live under `d<parent>`, inode attributes under `i<ino>`, and edge buffers contain a type byte plus big-endian inode. `scriptResolve` starts from `KEYS[1]` parent, resolves `KEYS[2]` path, checks uid `KEYS[3]`, and treats `ARGV` as supplementary gids.

## Dependencies And Integration Points

The scripts depend on Redis Lua `struct.unpack`, Redis hash/string commands, and exact binary layouts written by the Redis metadata engine and `Attr.Marshal`. They are consumed by Go Redis backend code that maps raised string errors to `syscall.Errno` values.

## Risks And Edge Cases

The 52-bit inode ceiling is critical because Redis Lua cannot exactly represent all uint64 values. `scriptResolve` does not follow symlinks by design and returns `ENOTSUP`, matching the `Meta.Resolve` contract for unsupported symlink-following. The permission check only checks execute permission on intermediate directories and relies on mode/ACL simplification available in the attr prefix; POSIX ACL behavior is not represented in the Lua script. Error spelling is `EACCESS`, so Go-side mapping must expect that exact string.

## Test Signals

No direct tests are in this file. Resolution behavior is indirectly exercised by Redis metadata tests, random filesystem operation tests when using Redis, and higher-level lookup/resolve/chroot paths.
