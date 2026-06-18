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
