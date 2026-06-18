# sources/cloud-native/buildkit/util/cachedigest/frame.go

## Purpose
Binary frame codec for cachedigest debug records. Frames encode a FrameID and payload length followed by payload bytes.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `FrameID, String, Frame, encodeFrames, decodeFrames`.

## Control Flow, State, And Persistence
encodeFrames appends big-endian id/length/data records; decodeFrames walks the byte slice and rejects truncated headers or payload overruns with ErrInvalidEncoding.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is format compatibility and memory use proportional to encoded payloads. db_test.go validates round-trip and invalid inputs.
