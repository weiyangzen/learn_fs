# sources/cloud-native/moby/daemon/logger/jsonfilelog/fuzz_test.go

Purpose: fuzzes JSON file log decoding against arbitrary byte input.

Important APIs/types/functions: `FuzzLoggerDecode` seeds with a valid JSON log line, creates a decoder via `decodeFunc`, and calls `Decode` against fuzz data.

Control flow/state/persistence: in-memory reader only. It checks that malformed inputs do not panic.

Dependencies/integration: targets `jsonfilelog/read.go` decoder and `jsonlog.JSONLog` unmarshaling.

Risks: fuzz test does not assert semantic output, only robustness.

Test signals: useful panic-safety signal for untrusted/corrupt json-file logs.
