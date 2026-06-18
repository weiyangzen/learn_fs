## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/prefetch.go

Purpose: shared flags and parsing for embedding prefetch file paths in SOCI metadata.

Important APIs/types/functions: `PrefetchFlags`, `ParsePrefetchFiles`, `loadPrefetchFilesFromJSON`, and `trimAndFilterFiles`.

Control flow: collect repeated `--prefetch-file` values, trim/filter blank entries, optionally read JSON array from `--prefetch-files-json`, trim/filter those, and return combined paths.

State and persistence: reads a JSON file when configured; no writes.

Dependencies and integration: used by create/convert builder option construction to call `soci.WithPrefetchPaths`.

Risks and test signals: no deduplication or path normalization; JSON must be a raw string array. No direct tests here.
