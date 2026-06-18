# sources/cloud-native/buildkit/util/cachedigest/db.go

## Purpose
Bolt-backed debug database for mapping content digests to encoded debug frames. It supports default DB registration, async frame persistence, lookup, and iteration.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `ErrInvalidEncoding, ErrNotFound, bucketName, DB, defaultDB, SetDefaultDB, GetDefaultDB, NewDB, Close, NewHash, FromBytes, saveFrames, ...`.

## Control Flow, State, And Persistence
NewDB opens bbolt; FromBytes and Hash.Sum call saveFrames asynchronously via WaitGroup; Get/All parse digest keys, decode frames, and return type plus data/skip frames. Close waits before closing.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/opencontainers/go-digest, github.com/pkg/errors, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are async writes needing Wait/Close, corrupt frame data, and nil DB returning not found/no-op. db_test.go covers FromBytes, NewHash, frame decoding, invalid encodings, and All.
