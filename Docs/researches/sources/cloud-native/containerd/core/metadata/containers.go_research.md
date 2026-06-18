# sources/cloud-native/containerd/core/metadata/containers.go

## Purpose

This file implements the metadata-backed container store. It persists container records in bbolt, supports filters, field-mask updates, validation, tracing, and marks metadata dirty when containers are deleted.

## Important APIs, Types, and Functions

`NewContainerStore(db)` returns a `containers.Store`. `containerStore` implements `Get`, `List`, `Create`, `Update`, and `Delete`. Internal helpers are `validateContainer`, `readContainer`, and `writeContainer`. It stores specs/runtime options/extensions as protobuf Any data and labels/timestamps through `boltutil`.

## Control Flow

Every public method requires a namespace from context. `Get` reads one bucket and unmarshals a container. `List` parses filters, iterates namespace container buckets, reads each record, and applies `adaptContainer`. `Create` validates input, creates a new container bucket, sets timestamps, and writes fields. `Update` loads the existing record, applies field paths for labels, extensions, spec, image, and snapshot key, rejects immutable changes on full replace, validates, updates `UpdatedAt`, and writes back. `Delete` deletes the bucket and increments the DB dirty counter.

## State and Persistence Behavior

Container records live under `v1/<namespace>/containers/<id>`. Stored fields include timestamps, spec Any, image, snapshotter, snapshot key, runtime name/options, extensions, sandbox ID, and labels. Deletion removes the metadata record but does not directly delete snapshots/content; dirty state triggers later GC.

## Dependencies and Integration Points

It integrates with core container types, metadata bucket helpers, `boltutil`, filters, namespace context, identifier and label validation, protobuf/typeurl, tracing, errdefs, and bbolt errors. GC uses container records as roots to retain referenced snapshots and labeled references.

## Risks and Edge Cases

Full updates only permit selected mutable fields and explicitly reject runtime name and snapshotter changes. Field paths are stringly typed and lower-case names such as `snapshotkey`. Label and extension subfield updates create maps if needed and can delete labels by writing empty values through `WriteLabels`. `writeContainer` deletes and recreates the runtime bucket but `WriteExtensions` may leave stale extension data if callers pass empty extension maps without deleting the bucket first.

## Test Signals

`containers_test.go` covers list filters, create/update/delete, invalid updates, immutable fields, label deletion, extensions, timestamps, and validation errors. Additional tests should cover sandbox ID persistence, runtime options round trip, stale extension removal, and GC retention of container snapshots.
