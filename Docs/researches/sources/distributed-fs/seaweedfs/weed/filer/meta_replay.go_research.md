# sources/distributed-fs/seaweedfs/weed/filer/meta_replay.go

## Purpose

`meta_replay.go` applies one metadata event from a subscribed filer stream to a `FilerStore`. It is the low-level replay primitive used by metadata aggregation and replication.

## Important APIs, Types, and Functions

The single public function is `Replay(filerStore FilerStore, resp *filer_pb.SubscribeMetadataResponse) error`.

## Control Flow

`Replay` reads `resp.EventNotification`. If `OldEntry` is present, it constructs the old full path from `resp.Directory` and old name, then deletes that entry from the store. If `NewEntry` is present, it chooses `message.NewParentPath` when set, otherwise `resp.Directory`, converts the protobuf entry to a filer `Entry`, and inserts it into the store.

## State and Persistence Behavior

All persistence is delegated to `DeleteEntry` and `InsertEntry` on the supplied store. The function does not open transactions, so rename-like delete/create events are only as atomic as the underlying event and store operations make them.

## Dependencies and Integration Points

The file depends on filer protobuf event shapes, `FromPbEntry`, SeaweedFS path utilities, and the shared `FilerStore` interface. It is called by `MetaAggregator` for remote metadata replication.

## Risks and Edge Cases

The function assumes `resp` and `EventNotification` are non-nil; callers must filter freshness events. Delete happens before insert, so a failure between steps can leave partial replay for move/update events. `InsertEntry` is used for new entries, so stores must treat insert as upsert or replay duplicates may fail.

## Test Signals

Tests should cover delete-only, create-only, rename with `NewParentPath`, update replacement, duplicate replay idempotence, nil event handling at caller boundaries, and partial failure behavior.
