# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/cursor_test.go

Purpose: unit tests for `FilerCursorPersister`.

Important APIs/types: `fakeStore` implements `dispatcher.FilerStore`; tests call `Load` and `Save`.

Control flow: fake store stores files by `dir/name`, returns copies, and returns `filer_pb.ErrNotFound` when absent. Tests exercise save/load and malformed payload paths.

State and persistence behavior: validates one JSON cursor per shard, isolation by filename, and strict corruption rejection for empty, non-JSON, wrong version, wrong shard id, short hashes, and nil store.

Dependencies and integration points: uses `filer_pb.ErrNotFound`, testify `require/assert`, and the real cursor JSON encoder/decoder.

Risks: fake store does not model partial writes or filer consistency. Tests do not assert JSON indentation or exact filename beyond paths used in setup.

Test signals: strong guard for cursor validation, which is load-bearing for avoiding accidental cursor rewind or corruption masking.
