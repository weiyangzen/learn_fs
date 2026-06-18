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
