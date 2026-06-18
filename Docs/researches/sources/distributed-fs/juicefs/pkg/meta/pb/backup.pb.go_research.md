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
