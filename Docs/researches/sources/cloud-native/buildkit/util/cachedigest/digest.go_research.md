# sources/cloud-native/buildkit/util/cachedigest/digest.go

## Purpose
Hash wrapper that records debug frames while computing sha256 digests. It can omit sensitive/noisy data through skip frames and recursively load sub-records referenced by digest strings.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `Type, String, NewHash, FromBytes, Hash, Reset, BlockSize, Size, Write, WriteNoDebug, Sum, Record, ...`.

## Control Flow, State, And Persistence
Write stores data frames, WriteNoDebug coalesces little-endian skip lengths, Sum persists typed frames, and Record.LoadSubRecords scans string/digest-list/file-list payloads for sha256 references and loads them recursively.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/bklog, github.com/opencontainers/go-digest`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are recursive graph growth, malformed file-list entries, and warnings rather than hard failures for missing subrecords. db_test.go covers hash recording and skip coalescing.
