<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go -->
# sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go

Purpose: tests progress reader close behavior.

Important APIs and types: `TestOutputOnPrematureClose` and `TestCompleteSilently`.

Control flow: the premature-close test reads only part of a short stream, drains prior progress, closes the reader, and expects a new progress update. The complete test reads all bytes, drains progress, closes, and expects no new update.

State and persistence: in-memory `bytes.Reader` and buffered channel.

Dependencies and integration: validates interaction between `NewProgressReader`, `ChanOutput`, `Read`, and `Close`.

Risks: tests do not verify rate limiting, exact progress fields, or underlying close errors.

Test signals: focused regression signal for user-visible progress completion behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader_test.go -->
