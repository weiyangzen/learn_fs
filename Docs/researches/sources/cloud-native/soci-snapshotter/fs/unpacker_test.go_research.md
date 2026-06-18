# sources/cloud-native/soci-snapshotter/fs/unpacker_test.go

Purpose: tests `layerUnpacker` control flow and `AsyncTeeReader` behavior with fake fetcher/archive implementations and in-memory readers/writers.

Important APIs and flow: `TestFailureModes` forces first fetch, store, and apply failures and asserts the expected calls occurred. `TestUnpackHappyPath` verifies local layers skip `Store` and remote layers are stored then fetched again before apply. Fake types implement `Fetcher` and `Archive` with counters. `TestAsyncTeeReader` checks basic, empty, erroring, and large inputs; the test writer captures tee output and close signaling. Benchmarks compare asynchronous teeing against `io.TeeReader` under artificial delays.

State and persistence: all state is test-local counters and buffers. No real filesystem unpack, digest verification, or containerd mount occurs.

Dependencies and integration: uses containerd mount/archive types only for interface signatures and fake lowerdir options. It validates unpacker orchestration rather than real tar application.

Risks and test signals: the tests strongly cover fetch/store/apply sequencing and tee read-error propagation. They do not assert archive apply options, actual whiteout conversion, digest verifier behavior, or writer-error handling in `AsyncTeeReader`.
