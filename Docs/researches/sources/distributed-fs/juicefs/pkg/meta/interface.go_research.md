# sources/distributed-fs/juicefs/pkg/meta/interface.go

## Purpose

`interface.go` defines the central JuiceFS metadata API: public constants, core metadata structs, attribute binary encoding, inode helpers, the `Meta` interface implemented by all metadata engines, driver registration, credential injection helpers, and `NewClient` construction.

## Important APIs, Types, And Functions

Constants define metadata protocol versions, chunk sizing (`ChunkBits`, `ChunkSize`), internal message types (`DeleteSlice`, `CompactChunk`, `Rmr`, `InfoV2`, etc.), node types, rename flags, setattr masks, inode flags, quota commands, name/symlink limits, root/trash inodes, and default recursive-remove threads.

`Ino` wraps inode IDs with `String`, `IsValid`, `IsTrash`, and `IsNormal`. `Attr` is the runtime inode attribute record. `Attr.Marshal` writes a compact binary representation using `utils.Buffer`; it encodes flags, type+mode, ownership, timestamps, nlink, length, rdev, parent, optional ACL IDs, and optional storage tier. `Attr.Unmarshal` reads the format with backward-compatible optional fields and marks attributes `Full`.

`typeToStatType`, `typeToString`, and `typeFromString` bridge JuiceFS node types to syscall modes and dump strings. `Entry`, `Slice`, `Summary`, `TreeSummary`, `SessionInfo`, `Flock`, `Plock`, and `Session` are shared API payloads.

`Meta` is the large engine contract covering lifecycle, sessions, deleted object scans, locks, trash cleanup, stats, permission and namespace operations, file I/O/chunks, xattrs, flock/plock, compaction, slices, recursive remove, summaries, clone, path lookup, integrity check/repair, chroot, format reload callbacks, quota handling, dump/load V1 and V2, metrics, ACLs, Kerberos tokens, and changelog scanning.

Driver support is provided by `Creator`, `metaDrivers`, `Register`, and `NewClient`. `injectPasswordIntoURI`, `readPasswordFromFile`, and `setPasswordFromEnv` add database passwords for MySQL/Postgres from `META_PASSWORD` or `META_PASSWORD_FILE`.

## Control Flow And State

`NewClient` normalizes bare addresses to `redis://`, extracts the driver before `://`, injects SQL passwords from environment/file when needed, logs a redacted address, validates/defaults config, looks up the registered creator, constructs an engine, and fatal-exits on invalid drivers or creation failure. Driver registration mutates the package-level `metaDrivers` map during init of backend packages.

`Attr.Marshal`/`Unmarshal` are persistence-critical: they define the binary schema used by metadata engines and V2 protobuf `Node.data`. Optional tail fields allow older stored attributes without ACL/tier data to still load.

## Dependencies And Integration Points

The file integrates with nearly every metadata engine and upper VFS layer through `Meta`. It depends on ACL types, Prometheus registerers, `utils`, Go `syscall`, `context`, URL escaping, and process environment. The dump/load APIs here connect to `dump.go`, V2 protobuf backup code, and engine-specific implementations.

## Risks And Edge Cases

`typeToStatType` and `typeFromString` panic on unknown types; callers must validate data before conversion. `metaDrivers` is a global map without synchronization, acceptable for init-time registration but not dynamic concurrent registration. `NewClient` uses fatal logging instead of returning errors, making initialization failures process-fatal. URI password injection uses `LastIndex("@")`; unusual usernames containing `@` are handled in tested ways but complex URI authority formats remain sensitive. `Attr.Marshal` size calculation must stay synchronized with optional fields.

## Test Signals

`interface_test.go` covers password injection, environment precedence, password file trimming/errors, and special SQL URI shapes. `load_dump_test.go`, `random_test.go`, and engine tests exercise most `Meta` methods indirectly.
