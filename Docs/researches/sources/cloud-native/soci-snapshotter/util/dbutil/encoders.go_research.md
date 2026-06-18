# sources/cloud-native/soci-snapshotter/util/dbutil/encoders.go

Purpose: this file provides varint encoding/decoding helpers for integer values stored in BoltDB buckets.

Important APIs: `EncodeInt(i int64) ([]byte, error)` encodes an int64 with `binary.PutVarint` and returns the used slice. `DecodeInt(data []byte) (int64, error)` decodes with `binary.Varint` and reports insufficient data or overflow when the decoded value is zero and the byte count indicates an error.

Control flow: encoding uses a fixed stack buffer of `binary.MaxVarintLen64`. Decoding relies on `binary.Varint`'s byte-count result: `n == 0` means too little data, `n < 0` means overflow.

State and persistence: no internal state. The encoded bytes are used by artifact DB fields such as size and span size.

Dependencies and integration points: used by `soci/artifacts.go` to persist `ArtifactEntry.Size` and `SpanSize`.

Risks: error detection is conditional on `i == 0`; this matches `binary.Varint` behavior for invalid inputs that return zero, but readers should understand that valid encoded zero also returns `n > 0` and no error. There are no tests in this subset specifically for negative values, zero, overflow, or truncated buffers.

Test signals: indirect coverage through artifact entry round trips; no direct unit tests.
