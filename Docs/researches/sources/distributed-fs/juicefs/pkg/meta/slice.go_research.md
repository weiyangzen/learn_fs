# sources/distributed-fs/juicefs/pkg/meta/slice.go

## Purpose

`slice.go` defines the in-memory and serialized representation for JuiceFS chunk slice records. It provides helpers to encode/decode slice metadata, overlay slice writes into a logical chunk view, compact chunk state, and decide how many old slice records can be skipped during compaction.

## Important APIs, Types, and Functions

The internal `slice` type stores object slice ID, object size, object offset, logical length, logical position within a chunk, and temporary binary-tree links. `newSlice`, `read`, `cut`, and `visit` build and traverse overlay trees. `sliceBytes` is the fixed serialized size, 24 bytes. `marshalSlice`, `readSlices`, and `readSliceBuf` encode/decode Redis list values or byte buffers. `buildSlice`, `compactChunk`, and `skipSome` are the main logical-layout helpers.

## Control Flow

Each serialized record is laid out as position, slice ID, size, offset, and length. `buildSlice` replays slice records in order; each new slice cuts the current root at its start and end, keeps the covered right side as the new node's right subtree, and makes the new slice the root. An in-order visit then emits logical `Slice` ranges, inserting zero-hole records when positions skip ahead. `compactChunk` removes leading and trailing zero-hole ranges, keeps a one-byte zero if the entire compacted result is a hole, and returns starting position, compacted size, and slice list. `skipSome` avoids compacting large useful first records when doing so would not materially reduce chunk state.

## State and Persistence Behavior

This file persists no state itself, but its 24-byte format is the on-disk/on-Redis contract for chunk list entries used by `redis.go`, backup/load code, compaction, cloning, copy-file-range, and GC. Slice ID zero represents holes or zero-filled ranges rather than object data. Because serialized layout is fixed and shared across engines and dumps, any incompatible change would require migration support.

## Dependencies and Integration Points

It depends only on `pkg/utils` buffers and the public `Slice` type. Redis metadata code uses `marshalSlice` for writes, truncate, fallocate, copy, clone, compaction, and load; `readSlices` is used for reads, listing, copy, clone, dump, cleanup, and reference accounting. Protobuf backup uses `sliceBytes` to pack raw chunk slices.

## Risks and Edge Cases

Corrupt serialized lengths return nil and force callers to handle `EIO` or skip corrupted chunks. The overlay algorithm mutates temporary copies of slice records, so callers must not reuse the tree links for persistent state. Zero-length slices are dropped by `newSlice`. Very large or highly fragmented chunk histories can produce deep recursive `cut`/`visit` traversal and high memory churn. `skipSome` is heuristic and can trade compaction opportunity for avoiding unnecessary rewrite of large first slices.

## Test Signals

Tests should cover marshal/read round trips, invalid buffer length handling, overlapping writes, hole insertion, truncation-style zero records, complete-hole compaction, leading/trailing hole trimming, repeated identical slices, and `skipSome` thresholds around 1 MiB and 5x size comparisons. Integration tests should verify Redis reads, writes, copy-file-range, clone, compaction, dump/load, and GC all interpret the same layout.
