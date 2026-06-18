# sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader_test.go

Purpose: this file verifies byte-position tracking for `PositionTrackerReader`.

Important helpers and tests: `bs` is a fixed byte slice. The helper `copy` fills buffers from `bs` and errors if the buffer is too short. `testReader` returns a configured byte count and error. `TestPositionTrackingReader` covers a full read from `bytes.Reader`, a short successful read, and a short read with `io.ErrUnexpectedEOF`.

Control flow and state: each case creates a new tracker, reads into a 10-byte buffer once, then checks `CurrentPos` and expected error matching with `errors.Is`.

Dependencies and integration points: tests only the local ioutils wrapper.

Risks and gaps: tests do not cover multiple reads accumulating position, zero-byte reads, EOF after all data, concurrent reads, or underlying readers that return `n=0` with an error. The package-level helper named `copy` shadows the builtin, but only within this test file.

Test signal quality: good for the key contract that bytes returned before an error still advance position; limited for repeated-read behavior.
