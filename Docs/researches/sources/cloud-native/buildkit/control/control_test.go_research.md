# Research: sources/cloud-native/buildkit/control/control_test.go

Purpose: unit-tests helper logic used by the control service solve path for cache exporter deduplication and cache export ignore-error parsing.

Important flow: `TestDuplicateCacheOptions` covers unique registry/local cache exports, duplicate registry/local entries, and special inline handling that keeps only the first inline exporter even with attrs. It asserts both duplicate lists and rest lists. `TestParseCacheExportIgnoreError` checks accepted bool spellings and unsupported malformed strings.

State and dependencies: no persistence; tests use in-memory protobuf cache option structs and testify assertions.

Risks and test signals: these helpers guard user-facing solve validation. Duplicate detection affects whether solves are rejected, and inline handling is intentionally permissive. The tests do not cover `cacheOptKey` hash failures or full solve integration.
