# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader_test.go

Purpose: tests reader path extraction and event dispatch behavior.

Important tests: create path extracts nested bucket/key; top-level object extraction; delete uses old entry; delete with empty new parent falls back to response directory; outside-bucket paths are skipped; bucket root events work with `/buckets/` and bare `/buckets`; `dispatchOne` filters nonmatching shards and emits matching shard events; context cancellation unblocks a send to an unbuffered channel.

Control flow/state: tests call private methods directly within package. They construct filer metadata responses and channels, then inspect emitted `Event` fields and processed counts.

Dependencies/integration: uses filer protobuf metadata response shapes and lifecycle `ShardID`.

Risks/gaps: `Run` streaming loop and batched event handling are not fully fake-stream tested here, though validation is covered in composition tests. Path extraction coverage is strong for known filer shapes.

Test signals: good signal for bucket/key reconstruction and shard gating, both central to avoiding misrouted lifecycle work.
