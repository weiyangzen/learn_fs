## sources/distributed-fs/juicefs/pkg/meta/backup.go

Purpose: defines JuiceFS metadata backup serialization primitives and options for dump/load workflows.

Important APIs/types/functions: constants define backup magic/version/EOS and segment type IDs. `SegType2Name` maps segment IDs to names. `getMessageFromType` and `createMessageByName` instantiate protobuf messages. `BakFormat` tracks current write position and footer; `writeSegment` serializes a `BakSegment`, records footer offsets/counts, and advances position; `ReadSegment`, `writeFooter`, `writeEOS`, and `ReadFooter` handle stream boundaries and footer access. `BakFooter.Marshal/Unmarshal` writes/reads protobuf footer plus trailing 8-byte length. `BakSegment` stores type, length, and protobuf value; `newBakSegment` infers segment type from `pb.Format` or populated `pb.Batch` field; `num` counts records; `Marshal` writes type/length/data; `Unmarshal` reads them and returns `errBakEOF` on EOS. `DumpOption` and `LoadOption` normalize thread counts; `dumpFormat` writes sanitized or secret-preserving format JSON; `dumpResult` sends results with context cancellation.

Control flow and state: backup files are `BakSegment... + BakEOS + BakFooter`. Footer infos accumulate offsets and counts by segment name for later indexed reading/validation. Segment payloads are protobuf; format payload embeds JSON bytes of filesystem format.

Dependencies and integration points: depends on JuiceFS metadata protobufs, `protojson`, global protobuf registry, binary big-endian encoding, `baseMeta.GetFormat`, and context-aware dump pipelines. Transaction marker key types are declared for later context use.

Risks and test signals: `io.Reader.Read` is used once for segment/footer payloads and may under-read on non-buffered readers; robust callers may need `io.ReadFull`. Error checks on writes use `err != nil && n != expected`, which can miss short writes with nil error. Segment type inference assumes exactly one populated `pb.Batch` field. Secret stripping in `dumpFormat` is critical for safe backups.
