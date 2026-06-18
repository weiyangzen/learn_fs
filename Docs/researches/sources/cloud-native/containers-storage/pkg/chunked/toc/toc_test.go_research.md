## sources/cloud-native/containers-storage/pkg/chunked/toc/toc_test.go

Purpose: unit tests for format-neutral TOC digest extraction.

Important APIs/types/functions: `TestGetTOCDigest` with valid, invalid, and empty annotation cases.

Control flow: constructs annotation maps and checks digest pointer content, error behavior, and nil result.

State and persistence: pure in-memory tests.

Dependencies and integration points: protects `toc.GetTOCDigest` consumers in chunked conversion and manifest handling.

Risks: missing tests for zstd:chunked annotation and conflict handling leave two branches uncovered.

Test signals: basic digest parsing regression signal; local execution blocked because `go` is unavailable.
