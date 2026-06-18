# sources/cloud-native/nydus-snapshotter/pkg/cache/manager_test.go

Purpose: verifies blob ID extraction from cache filenames with known nydus cache suffixes.

Important APIs and functions: `TestExtractBlobIDFromFilename` table-tests `ExtractBlobIDFromFilename`.

Control flow: cases cover plain blob IDs, each known suffix, combined `.blob.data.chunk_map`, real SHA-256-like names, empty input, unknown suffixes, names with unrelated dots, and suffix precedence.

State and persistence: pure function test with no filesystem state.

Dependencies and integration points: uses testify assertions only.

Risks and gaps: no tests cover `NewManager`, `CacheUsage`, or `RemoveBlobCache`, so filesystem behavior, missing-file handling, and deletion order are unverified in this subset.

Test signals: good coverage of filename parsing edge cases and suffix ordering.
