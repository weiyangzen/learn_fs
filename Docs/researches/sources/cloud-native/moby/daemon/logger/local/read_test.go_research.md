# sources/cloud-native/moby/daemon/logger/local/read_test.go

Purpose: tests local decoder behavior around incomplete records.

Important APIs/types/functions: `TestDecodeIncompleteRecord` verifies that `Decode` returns `io.EOF` for a partial record and succeeds after the rest is appended.

Control flow/state/persistence: test simulates a log file being extended while a decoder has already seen an incomplete record.

Dependencies/integration: targets `local.decoder.readRecord` and `Decode`.

Risks: this behavior is important for following active files; retries must not hide permanent corruption indefinitely.

Test signals: direct signal for append-in-progress resilience.
