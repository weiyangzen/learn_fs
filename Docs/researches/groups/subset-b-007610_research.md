# Research: subset-b-007610

Grouped research for JuiceFS metadata files in `sources/distributed-fs/juicefs/pkg/meta`. Each section is source-tree-aligned and can be split directly into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/dump.go -->
# sources/distributed-fs/juicefs/pkg/meta/dump.go

## Purpose

`dump.go` defines the legacy JSON metadata dump/load data model and parser helpers for JuiceFS metadata. It serializes the logical filesystem tree, counters, sustained/deleted files, directory/user/group quotas, changelog entries, xattrs, symlinks, chunks, and POSIX ACLs into `DumpedMeta`, then reconstructs store-side metadata by walking a JSON stream.

## Important APIs, Types, And Functions

The primary exported-ish data structures are `DumpedMeta`, `DumpedEntry`, `DumpedAttr`, `DumpedChunk`, `DumpedSlice`, `DumpedXattr`, `DumpedQuota`, `DumpedACL`, `DumpedCounters`, `DumpedSustained`, `DumpedDelFile`, and `DumpedChangeLog`. They are JSON-facing representations, distinct from runtime `Attr`, `Slice`, `Quota`, and ACL objects.

`escape` and `unescape` preserve arbitrary byte names and xattr values in JSON by percent-encoding invalid UTF-8, control/space bytes, `%`, quotes, and backslashes. `DumpedEntry.writeJSON` and `writeJsonWithOutEntry` stream JSON directly to a buffered writer rather than building a full tree string. `DumpedMeta.writeJsonWithOutTree` writes the top-level metadata object without `FSTree`/`Trash` so tree entries can be appended by traversal code elsewhere.

`loadEntries` is the main streaming loader entry point. It decodes top-level JSON tokens, rebuilds counters and slice refs, and dispatches `FSTree`/`Trash` to `decodeEntry`. `decodeEntry` recursively decodes one tree node, normalizes root/subdir loading, tracks parent lists for hardlinks, rebuilds `UsedSpace`, `UsedInodes`, `NextInode`, `NextTrash`, `NextChunk`, dir quota usage, and invokes callbacks for each unique loaded inode and chunk. `dumpAttr`/`loadAttr` translate between runtime `Attr` and JSON `DumpedAttr`; `dumpACL`/`loadACL` translate ACL rules.

## Control Flow And Persistence

Dump output is tree-oriented JSON. Load input is token-streamed with `goccy/go-json.Decoder`; this avoids requiring the entire metadata tree in memory. Counters from the dump are read for progress and validation, but loader counters are rebuilt from decoded entries and chunks. Each unique inode is loaded once (`len(e.Parents) == 1`) so hardlinked files are represented by additional parent references rather than duplicate node writes.

Quota persistence is special: JSON `DumpedQuota` does not expose used fields, but `decodeEntry` recomputes dir quota usage while traversing descendants. `baseMeta.loadDumpedQuotas` writes directory, user, and group quotas through `m.en.doSetQuota`; if user/group quota maps exist it temporarily installs the dump format and runs `ScanUserGroupUsage` to rebuild actual usage.

## Dependencies And Integration Points

This file depends on `aclAPI`, `utils.Buffer`/progress bars, `typeToString`/`typeFromString`, `align4K`, `baseMeta.en` engine methods, and the broader dump/load methods implemented by engine-specific metadata code. It integrates with ACL storage by converting rules to compact JSON ACL entries and with chunk GC/reference accounting through `chunkKey` callbacks.

## Risks And Edge Cases

Name/value escaping is compatibility-critical: malformed percent escapes are intentionally left as literal bytes by `unescape`, while valid escapes are decoded. `typeFromString` panics on unknown types, so corrupt dumps can crash unless errors are caught before conversion. `writeJSON` mutates `DumpedXattr.Value` by replacing it with its escaped form, which is safe for one-shot dump entries but risky if callers reuse objects. The loader assumes directory tree shape for quota propagation and uses only the first parent when walking quota ancestors, so hardlink and multi-parent behavior must stay consistent with JuiceFS semantics.

## Test Signals

`load_dump_test.go` exercises `escape`/`unescape` with UTF-8, GBK bytes, spaces, `%`, quotes, and backslashes; validates restored counters, hardlinks, symlinks, xattrs, ACLs, chunks, dir stats, and quotas; and compares legacy dump output against sample files. `random_test.go` indirectly stresses dump-relevant metadata invariants through generated filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/dump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/info.go -->
# sources/distributed-fs/juicefs/pkg/meta/info.go

## Purpose

`info.go` parses selected Redis/KeyDB `INFO` fields and enforces minimum compatibility assumptions for Redis-backed metadata. It is a small safety layer used during metadata client setup to warn about durability-sensitive Redis settings and reject too-old server versions.

## Important APIs, Types, And Functions

`redisVersion` stores the original version string plus parsed `major` and `minor` numbers. `oldestSupportedVer` is `4.0.x`. `parseRedisVersion` splits a string on `.`, requires at least major/minor components, parses the first two components with `strconv.Atoi`, and preserves the original string for logging. `redisVersion.olderThan` compares major, then minor. `String` returns the original version string.

`redisInfo` stores four parsed fields: `aofEnabled`, `maxMemoryPolicy`, `redisVersion`, and `storageProvider`. `checkRedisInfo` scans a raw `INFO` response line by line, skips blank/comment lines, splits `key:value`, and handles `aof_enabled`, `maxmemory_policy`, `redis_version`, and `storage_provider`. For Redis version parsing errors it logs a warning; for a parsed version older than `oldestSupportedVer` it calls `logger.Fatalf`. For `aof_enabled:0` it logs a data-loss warning. For `storage_provider`, only `flash` is retained; `none` and absent values collapse to the empty string.

## Control Flow And State

The parser is stateless and returns a `redisInfo` value plus an error, although normal malformed non-version lines are ignored rather than surfaced. Fatal version rejection is process-level behavior through the logger, not an ordinary returned error. This means callers cannot recover from too-old Redis unless the logger fatal behavior is intercepted in tests.

## Dependencies And Integration Points

The file depends only on `fmt`, `strconv`, `strings`, and the package logger. It is tied to Redis metadata backends and likely called by Redis client initialization code after fetching server info. The `storageProvider` field supports KeyDB/flash distinctions without exposing provider-specific parsing elsewhere.

## Risks And Edge Cases

Only major/minor are compared; patch and prerelease/build metadata are ignored. Version strings such as `6.2.19` parse, while `3` or nonnumeric components fail. On parse failure the warning currently formats the zero-value parsed version rather than the raw string in the `%q` slot, which may make diagnostics less clear. `checkRedisInfo` does not enforce `maxmemory_policy` or AOF, it only records/warns, so higher-level code must decide how to react.

## Test Signals

`info_test.go` covers `olderThan`, invalid/valid version parsing, `String`, and a large representative Redis `INFO` payload where `redis_version`, `aof_enabled`, and `maxmemory_policy` are extracted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/info_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/info_test.go

## Purpose

`info_test.go` provides focused unit coverage for Redis version comparison, Redis version parsing, and parsing of selected fields from a raw Redis `INFO` response.

## Important Tests

`TestOlderThan` constructs `redisVersion{"2.2.10", 2, 2}` and checks comparison against newer major, newer minor, same version, older minor, itself, and the zero value. It asserts that comparison uses only major/minor ordering and that equality is not considered older.

`TestParseRedisVersion` has an invalid subtest with empty, nonnumeric, and missing-minor strings, all expected to return errors. Its valid subtest parses `6.2.19`, verifies `major == 6`, `minor == 2`, and confirms `String()` preserves the full original patch version.

`TestParseRedisInfo` embeds a large multiline Redis `INFO` fixture covering many sections. It calls `checkRedisInfo` and asserts `redisVersion == "6.1.240"`, `aofEnabled == false`, and `maxMemoryPolicy == "allkeys-lru"`.

## Control Flow And Test Data

The tests use standard Go `testing` subtests and fatal assertions. The large INFO fixture intentionally includes comments, indentation, unrelated fields, and `aof_enabled:0`, exercising line trimming, comment skipping, and selective field extraction. It does not assert on warning logs.

## Dependencies And Integration Points

The tests are same-package (`package meta`), so they access unexported `redisVersion`, `parseRedisVersion`, and `checkRedisInfo` directly. They serve as regression coverage for Redis backend initialization logic without requiring a live Redis instance.

## Risks And Gaps

No test covers a too-old but parseable version because `checkRedisInfo` calls `logger.Fatalf`, which is hard to assert without intercepting process exit/fatal behavior. `storage_provider:flash` behavior is not tested. The warning path for malformed `redis_version` inside `INFO` is not checked. The tests also do not verify `maxmemory_policy` handling beyond storing the value; any policy validation would need separate coverage.

## Test Signals

These tests are low-cost unit tests and should be run with normal package tests. They primarily signal parser stability and guard against accidental changes in major/minor comparison semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/interface.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/interface_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/interface_test.go

## Purpose

`interface_test.go` verifies credential helper behavior used by `NewClient` for MySQL and Postgres metadata URIs. The coverage is focused on password injection, environment/file password sourcing, precedence, whitespace trimming, and error handling.

## Important Tests

`Test_injectPasswordIntoURI` supplies `dbPasswd` to SQL URI shapes. It confirms existing passwords are preserved; empty or absent passwords are inserted; MySQL socket-style authorities and Postgres host/socket URLs work; missing `@` and malformed userinfo with too many colon-separated fields error. It also documents edge handling for usernames containing `@`, because the helper uses the last `@` as authority terminator.

`Test_setPasswordFromEnv` creates a temporary password file and exercises `META_PASSWORD`, `META_PASSWORD_FILE`, both variables together, neither variable, and nonexistent password file. `META_PASSWORD` takes precedence over file content. Tests clean both environment variables before and after each case.

`Test_readPasswordFromFile` creates temporary files with plain passwords, surrounding whitespace, empty content, and special characters. It confirms `strings.TrimSpace` behavior and reports an error for missing files.

## Control Flow And State

All tests use temporary directories and same-package access to unexported helpers. Environment mutation is localized with `os.Unsetenv` and deferred cleanup, which prevents test pollution across subtests in normal serial execution.

## Dependencies And Integration Points

The tests touch only `os`, `filepath`, and `testing`; they avoid live database clients. They validate the pre-driver URI transformation path used by `NewClient` for `mysql` and `postgres` schemes.

## Risks And Gaps

The tests do not call `NewClient` itself, so they do not verify that password injection is applied only to SQL drivers or that redacted logging hides injected passwords. They do not test percent-escaping of password characters that need URL escaping, although `url.UserPassword` is used by the implementation. Since environment tests are not explicitly parallel-safe, adding `t.Parallel()` would be unsafe.

## Test Signals

These are deterministic unit tests. Failures indicate regressions in secure/noninteractive SQL metadata configuration, especially deployment flows that supply credentials through environment variables or mounted secret files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/interface_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/load_dump_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/load_dump_test.go

## Purpose

`load_dump_test.go` is integration and regression coverage for legacy JSON metadata dumps and V2 protobuf metadata backups. It loads sample metadata into multiple engines, validates restored semantics, dumps back to canonical sample files, restores across engines, and checks secret/trash behavior.

## Important APIs And Helpers

`TestEscape` validates `escape`/`unescape` with UTF-8 and GBK byte sequences, spaces, `%`, quotes, and backslashes. `Utf8ToGbk` and `GbkToUtf8` support those byte-level cases.

`checkMeta` is the main semantic validator. It loads format settings, checks counters (`usedSpace`, `totalInodes`, `nextInode`, `nextChunk`, `nextSession`, `nextTrash`) with Redis-specific counter offsets, reads root entries, validates GBK/UTF-8 names, computes and compares directory stats, validates root dir quota usage, validates user/group quota limits, checks file attributes/flags/ACL IDs, decodes access/default ACL rules, reads file chunks, verifies hardlink parents, reads GBK symlink targets, and checks xattrs.

`testLoad`, `testDump`, `testLoadDump`, `testLoadSub`, `testDumpV2`, `testLoadDumpV2`, `testLoadOtherEngine`, and `testSecretAndTrash` compose engine-specific load/dump/restore scenarios.

## Control Flow And Persistence

Legacy tests reset a metadata engine, call `LoadMeta` with `metadata.sample`, validate state, dump with `DumpMeta` in fast and non-fast modes, and compare output with `diff`. Chroot/subdir behavior is tested by dumping `d1` as root and by loading a subdir sample into a fresh engine.

V2 tests dump with `DumpMetaV2`, load with `LoadMetaV2`, and verify same semantic state. They also load V2 dumps from one engine into another to exercise backend-neutral protobuf persistence. `testSecretAndTrash` verifies `DumpOption.KeepSecret`: encryption keys survive when true and become `"removed"` when false; it also scans trash files and checks inode/size expectations.

## Dependencies And Integration Points

The tests depend on live/available metadata engines depending on test selection: Redis, SQLite, Badger, TiKV, etcd, Postgres, and memkv. They use package-level `NewClient`, engine internals (`m.getBase().en`, `engine.doGetQuota`, `engine.doGetDirStat`), ACL APIs, sample dump files, and shell `diff`.

## Risks And Edge Cases

These tests can be environment-sensitive: Redis/TiKV/etcd/Postgres addresses must exist for some cases, while `SKIP_NON_CORE` only gates slow tests. Shelling out to `diff` assumes a Unix-like environment. The V2 cross-engine tests write dump files into the working directory (`sqlite-secret.dump`, engine dumps, `test.dump`), which can leave artifacts if tests abort. Counter expectations include Redis-specific off-by-one behavior, documenting backend divergence.

## Test Signals

This is the strongest regression signal for dump/load compatibility. It covers binary names, hardlinks, ACLs, xattrs, chunks, quotas, dir stats, trash, secret stripping, chroot dump, and cross-engine V2 portability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/load_dump_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/lua_scripts.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/lua_scripts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/openfile.go -->
# sources/distributed-fs/juicefs/pkg/meta/openfile.go

## Purpose

`openfile.go` implements an in-memory open-file tracker and short-lived cache for attributes and chunk slice lists. It lets metadata clients reuse attributes for recently opened files, keep page cache hints stable, and avoid repeated chunk lookups while a file remains open or recently checked.

## Important APIs, Types, And Functions

`openFile` stores an `Attr`, reference count, last-check Unix timestamp, cached first chunk, and cached nonzero chunks. It has `invalidateChunk` and `release`; released instances return to `ofPool`.

`openfiles` owns a mutex, expiry duration, entry limit, and `map[Ino]*openFile`. `newOpenFiles` initializes the map and starts the background `cleanup` goroutine.

Public methods on the tracker are `OpenCheck`, `Open`, `Close`, `Check`, `Update`, `IsOpen`, `ReadChunk`, `CacheChunk`, `InvalidateChunk`, and `find`. Sentinel chunk indexes `invalidateAllChunks` and `invalidateAttrOnly` are defined, though this file only handles all/individual chunk invalidation.

## Control Flow And State

`OpenCheck` returns a cached attr and increments refs when an inode exists and `lastCheck` is within `expire`. `Open` creates or reuses an entry, preserves `KeepCache` if mtime/mtimensec match, invalidates chunks when attributes changed, stores the new attr, forces `KeepCache = true` for the next open, increments refs, and updates `lastCheck`. `Close` decrements refs and reports whether refs are now nonpositive or the file was unknown.

`Check` reads a cached attr without incrementing refs and panics if passed nil. `Update` updates cached attrs, invalidating chunk caches on mtime changes. Chunk cache methods store chunk zero in `first` and other chunks in the `chunks` map.

The cleanup goroutine periodically scans at most 1000 entries, removes long-idle (`refs <= 0` and last check older than 12 hours) entries, and if over `limit`, evicts least-recently checked non-open entries. Sleep duration scales with scan/deletion counts.

## Dependencies And Integration Points

This file depends on `sync`, `time`, package `Ino`, `Attr`, and `Slice`. It is used by metadata engines and VFS-facing open/read/write paths to coordinate open state with attr/chunk cache invalidation.

## Risks And Edge Cases

All map and openFile field access is serialized by the outer `openfiles` mutex; the embedded `openFile.RWMutex` is unused here. `Close` can decrement refs below zero if calls are unbalanced. `cleanup` has a subtle candidate eviction flow: when a newer least-recent candidate is found, it releases/deletes the previous candidate inside the loop, so changes need careful review to avoid deleting the wrong file. `find` returns a pointer after unlocking, so external mutation would race unless callers treat it as read-only or add locking.

## Test Signals

No direct tests are listed for this file. Behavior is indirectly tested by open/read/write metadata operations and randomized filesystem state-machine tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/openfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/pb/backup.pb.go -->
# sources/distributed-fs/juicefs/pkg/meta/pb/backup.pb.go

## Purpose

`backup.pb.go` is generated Go protobuf code for the JuiceFS metadata V2 backup schema in `backup.proto`. It provides concrete Go message structs, getters, reflection descriptors, raw descriptor compression, dependency indexes, and type-builder initialization used by dump/load V2 code.

## Important APIs And Types

The generated package is `pb`. Message structs are `Format`, `Counter`, `Sustained`, `DelFile`, `SliceRef`, `Acl`, `Xattr`, `Quota`, `Stat`, `Node`, `Edge`, `Parent`, `Chunk`, `Symlink`, `ChangeLog`, `Batch`, `Footer`, and nested `Footer_SegInfo`. Each has standard generated methods: `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters.

`Batch` is the central bulk transfer container and includes repeated lists for nodes, edges, chunks, slice refs, xattrs, parents, symlinks, sustained entries, deleted files, dir stats, dir quotas, ACLs, counters, changelogs, user quotas, and group quotas. `Footer` stores backup magic/version and a map from segment name to offsets/counts via `Footer_SegInfo`.

## Control Flow And Persistence

There is no handwritten business logic. The generated `init` calls `file_pkg_meta_pb_backup_proto_init`, which builds a `protoreflect.FileDescriptor` from the raw descriptor, message metadata, Go type table, and dependency indexes. After building, raw descriptor/type/dependency slices are nilled to reduce memory. `file_pkg_meta_pb_backup_proto_rawDescGZIP` lazily compresses the raw descriptor with `sync.Once`.

The persistence contract is defined by protobuf field numbers and wire types. The generated code serializes/deserializes opaque bytes for runtime-specific binary payloads such as `meta.Format` JSON, `meta.Attr` binary data, ACL binary rules, encoded chunk slices, symlink targets, xattr values, and changelog entries.

## Dependencies And Integration Points

The file depends on `google.golang.org/protobuf/reflect/protoreflect`, `runtime/protoimpl`, `reflect`, and `sync`. It is consumed by metadata V2 dump/load implementation files, including code that writes segment batches and reads footers.

## Risks And Edge Cases

Manual edits would be overwritten by `protoc`; schema changes must happen in `backup.proto`. Compatibility depends on never reusing field numbers incompatibly. Since many fields are opaque bytes, protobuf type safety does not validate nested JuiceFS binary formats; the loader must validate `Attr`, slices, ACLs, and format JSON separately. Generated getters return zero values for nil receivers, which can hide absent fields unless callers distinguish presence where needed.

## Test Signals

`load_dump_test.go` exercises this generated schema through `DumpMetaV2`/`LoadMetaV2`, cross-engine restore, secret stripping, trash scanning, ACLs, chunks, quotas, counters, and directory stats. There are no direct unit tests for generated accessors, which is normal for generated protobuf code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/pb/backup.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/pb/backup.proto -->
# sources/distributed-fs/juicefs/pkg/meta/pb/backup.proto

## Purpose

`backup.proto` defines the protobuf schema for JuiceFS metadata V2 backups. It is the authoritative wire contract used to generate `backup.pb.go` and to serialize backend-neutral metadata batches plus a footer index.

## Important Messages

`Format` stores the JSON form of `meta.Format`. `Counter` stores named counters. `Sustained` and `DelFile` preserve open-deleted/sustained file state and trash/deleted-file metadata. `SliceRef` stores object slice reference counts. `Acl` stores ACL rule binary data by ACL ID. `Xattr` stores inode xattr name/value pairs.

`Quota` stores quota key, limits, usage, and type; the same message is reused for directory, user, and group quota lists. `Stat` stores directory stats: inode, data length, used space, and used inodes. `Node` stores inode and binary `meta.Attr`; `Edge` stores directory parent/inode/name/type; `Parent` stores extra parent counts for Redis/TiKV hardlink tracking; `Chunk` stores inode/index plus encoded slice array; `Symlink` stores symlink target bytes; `ChangeLog` stores versioned changelog bytes.

`Batch` groups repeated metadata records by type. `Footer` contains `magic`, `version`, and a `map<string, SegInfo>` where each `SegInfo` records segment offsets and record counts.

## Control Flow And Persistence

The schema is proto3 with package `pb` and `go_package = "./pb"`. Field numbers in each message define the stable backup format. V2 dump code can write many `Batch` records and then a `Footer` that indexes named segments for load-time seeking and validation. Several fields intentionally use `bytes` because JuiceFS already has compact binary encodings for attrs, ACLs, chunks, names, symlink targets, and changelog entries.

## Dependencies And Integration Points

The file is consumed by `protoc --go_out=pkg/meta pkg/meta/pb/backup.proto` per its header comment. It integrates with `backup.pb.go` and the metadata V2 dump/load implementations. It mirrors runtime types in `pkg/meta`, including `Attr`, slice encoding, `Quota`, `dirStat`, ACL rules, and format JSON.

## Risks And Edge Cases

Backward compatibility depends on preserving field numbers and adding new fields only in protobuf-compatible ways. Because user/group quotas were appended to `Batch` as fields 15 and 16, older readers that ignore unknown fields can skip them, but older loaders will not restore those quotas. Opaque binary fields require the corresponding runtime binary formats to remain backward-compatible too; protobuf alone does not solve `Attr.Marshal` or slice encoding changes.

## Test Signals

`load_dump_test.go` is the principal integration coverage for this schema through V2 dump/load and cross-engine restore. Regenerating `backup.pb.go` should produce only generated-code changes aligned with this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/pb/backup.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/quota.go -->
# sources/distributed-fs/juicefs/pkg/meta/quota.go

## Purpose

`quota.go` implements directory stats, filesystem capacity checks, directory quotas, user quotas, group quotas, quota flushing, quota scans/repair, and Prometheus quota metrics for JuiceFS metadata. It is the central enforcement and reconciliation layer between in-memory quota counters and engine-persisted quota records.

## Important APIs, Types, And Functions

`dirStat` tracks directory `length`, `space`, and `inodes`. Quota types are `DirQuotaType`, `UserQuotaType`, `GroupQuotaType`, and `AllQuotaType`. `Quota` stores limits, persisted usage, and pending deltas (`newSpace`, `newInodes`). `Quota.check`, `update`, `snap`, and `sanitize` perform atomic limit checks and counter movement.

Directory stat paths include `calcDirStat`, `GetDirStat`, `updateDirStat`, `updateParentStat`, `flushDirStat`, and `doFlushDirStat`. Volume stats use `flushStats`, `doFlushStats`, and `syncVolumeStat`.

Quota enforcement uses `checkQuota`, `checkDirQuota`, `checkUserQuota`, `checkGroupQuota`, `updateDirQuota`, and `updateUserGroupStat`. Loading/flushing uses `loadQuotas`, `syncQuotaMaps`, `collectQuotas`, `updateQuota`, `flushQuotas`, and `doFlushQuotas`.

CLI/API quota handling is routed by `HandleQuota` into `handleQuotaSet`, `handleQuotaGet`, `handleQuotaList`, and `handleQuotaCheck`. Repair/reconciliation helpers include `calcDirQuotaUsage`, `ScanUserGroupUsage`, `scanGlobalUserGroupUsage`, `checkDirUsage`, `compareUGUsage`, `repairUsage`, `repairUgUsage`, and `checkUGUsage`. Metrics are maintained by `updateQuotaMetrics`, type-specific update helpers, and `cleanupQuotaMetrics`.

## Control Flow And Persistence

Quota enforcement first checks user and group quotas, then global capacity/inode limits, then ancestor directory quotas when `Format.DirStats` is enabled. Positive `space`/`inodes` deltas are rejected with `EDQUOT` for quota limits or `ENOSPC` for global volume limits. Updates are staged in `newSpace/newInodes` atomics and flushed asynchronously. `doFlushQuotas` snapshots pending deltas, persists them through `m.en.doFlushQuotas`, then moves deltas into `UsedSpace/UsedInodes` only after successful persistence.

Setting a directory quota enables `DirStats` in the format if needed, persists limits with unknown usage (`-1`), and if newly created, computes recursive usage through `GetSummary`. Setting user/group quota may enable `UserGroupQuota` and trigger a global usage scan. Scans walk root and optional trash, count directory/file ownership, de-duplicate hardlinked files, and include sustained inodes. Repair can clean and rewrite user/group usage records.

## Dependencies And Integration Points

This file is tightly coupled to `baseMeta`, engine methods (`doLoadQuotas`, `doSetQuota`, `doGetQuota`, `doFlushQuotas`, `doUpdateDirStat`, `doReaddir`, `doScanSustainedInodes`, `cleanUgUsage`, etc.), `Format` flags, path resolution, summaries, parent caches, metrics collectors, and human-readable logging via `go-humanize`.

## Risks And Edge Cases

Quota checks use pending deltas plus persisted usage, so failed flushes can keep enforcement conservative until persistence succeeds. `syncQuotaMaps` deletes missing directory quotas but intentionally does not delete missing user/group quotas, because user/group maps may contain usage-only records. Global user/group scans are expensive and can be affected by concurrent mutations. The scan counts directories as inodes and files by aligned length, but ignores non-file/non-directory sizes except sustained files. Trash inclusion depends on `TrashDays` and existence of `TrashInode`. Metrics cleanup must delete label values for removed/unlimited quotas to avoid stale series.

## Test Signals

`load_dump_test.go` validates restored dir/user/group quotas from sample metadata. `random_test.go` checks `StatFS` against a model and exercises operations that update quota-relevant stats. Dedicated quota tests are not in this subset, so scan/repair behavior relies on broader integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/quota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/random_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/random_test.go

## Purpose

`random_test.go` is a property-based state-machine test for the `Meta` interface. It builds an in-memory model of filesystem metadata (`fsMachine`) and uses `pgregory.net/rapid` to generate long random sequences of namespace, file, xattr, ACL, stat, and lock operations, comparing real metadata engine behavior against the model after each operation.

## Important Types And Model Functions

Model types include `tSlice`, `tQuota`, `tNode`, `tEntry`, and `fsMachine`. `tNode` models inode type, mode, uid/gid, timestamps, flags, length, parents/hardlink state, chunks, children, symlink target, xattrs, quotas, flocks, plocks, and ACLs. Permission helpers `accessMode`, `access`, and `stickyAccess` implement simplified POSIX/ACL checks.

`fsMachine.Init` creates a root model, initializes a real `Meta` client from `-rapid.meta` (default `memkv://jfs-unit-test`), resets/formats it, installs session/metrics state, and records backend type (`db`, `redis`, or `tkv`) to account for backend-specific errno ordering. `Cleanup` closes/reset/shuts down the real backend.

The model implements expected behavior for create/link/symlink/readlink/unlink/rmdir/lookup/getattr/truncate/fallocate/copy-file-range/rmr/rename/readdir/write/read/xattrs/tree checking/ACL/statfs/times/chmod/chown/flock/plock/list-locks/getlk/setlk.

## Control Flow And Test Coverage

Each exported method on `fsMachine` is a rapid action. It draws random inputs, calls the real `Meta` method, calls the model method, and fails if errno or returned data diverges. Enabled actions cover `Mkdir`, `Mknod`, `Link`, `Rmdir`, `Unlink`, `Symlink`, `Readlink`, `Lookup`, `Getattr`, `Rename`, `Readdir`, `Fallocate`, `Write`, `Read`, `SetXAttr`, `RemoveXattr`, `GetXAttr`, `ListXAttr`, `Check`, `Setfacl`, `GetACL`, `RemoveACL`, `StatFS`, `SetAmtime`, `Chmod`, `Chown`, `Flock`, `ListLocks`, `Getlk`, and `Setlk`. Truncate, copy-file-range, and recursive remove actions are present but disabled due to slice compaction/concurrency unpredictability.

`Check` recursively compares the full filesystem tree, attributes, chunks, symlinks, and xattrs. Lock methods also compare `ListLocks` results after successful updates. `TestFSOps` configures rapid defaults (`steps=200`, `checks=5000`, `shrinktime=1h`) and runs the state machine with logging reduced to errors.

## Dependencies And Integration Points

The test depends on `rapid`, ACL APIs, Prometheus metrics setup, package lock helpers (`ownerKey`, `plockRecord`, `updateLocks`), context constructors, test config/format helpers, and all registered metadata engines reachable through `NewClient`. It is same-package and touches internal session fields.

## Risks And Edge Cases

The model includes backend-specific conditional behavior because db/redis/tkv sometimes differ in validation order and returned errno. Some model checks are intentionally simplified or disabled, especially truncate/copy-file-range slice compaction and recursive remove concurrency. Name generation filters `|`, `.#`, and newline due to known metadata constraints. The test is powerful but can be slow and failure shrinking can take time; default check count is high. It mutates global flags and logger level, restoring them with defers.

## Test Signals

This is the broadest behavioral signal for `Meta` compatibility. Failures usually indicate a real metadata semantic regression, a backend-specific errno ordering change, or a model drift that needs explicit reconciliation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/random_test.go -->
