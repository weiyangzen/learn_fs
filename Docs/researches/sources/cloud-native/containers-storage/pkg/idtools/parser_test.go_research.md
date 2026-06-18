## sources/cloud-native/containers-storage/pkg/idtools/parser_test.go

Purpose: tests ID map string parsing for Unix builds.

Important APIs/types/functions: `TestParseIDMap`.

Control flow: table-driven cases call `ParseIDMap` with valid triplets, multiple entries, malformed fields, oversized values, and wrong colon structure, asserting error presence.

State and persistence: pure in-memory tests.

Dependencies and integration points: protects CLI/config parsing for ID mappings.

Risks: does not assert exact returned `IDMap` values for success cases, only absence of error. Does not cover packed multi-triplet single strings or zero-size mappings.

Test signals: basic validation signal; local execution blocked by missing `go`.
