# sources/cloud-native/buildkit/util/cachedigest/db_test.go

## Purpose
Unit tests for cachedigest DB/frame/hash behavior. They create temporary bbolt databases and reset the package default DB around each test.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `tempDB, TestFromBytesAndGet, TestNewHashAndGet, TestEncodeDecodeFrames, TestDecodeFramesInvalid, TestAll`.

## Control Flow, State, And Persistence
Tests cover FromBytes/Get, NewHash with WriteNoDebug skip coalescing, encode/decode round-trip, invalid frame encodings, and All iteration over multiple records.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/opencontainers/go-digest`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include async write waiting, frame endian handling, ErrNotFound, and ErrInvalidEncoding behavior.
