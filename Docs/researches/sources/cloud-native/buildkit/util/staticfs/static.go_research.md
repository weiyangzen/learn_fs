<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static.go -->
# sources/cloud-native/buildkit/util/staticfs/static.go

Purpose: provides an in-memory implementation of `fsutil.FS`.

Important APIs and types: `File`, `FS`, `NewFS`, `Add`, `Walk`, `Open`, `convertPathToKey`, and `convertKeyToPath`.

Control flow: `Add` normalizes leading slash, updates stat size/mode/path, and stores data by path. `Walk` filters keys by target prefix, sorts them using a slash-to-NUL key transform so parent/child order is stable, and calls the callback with `fsutil.DirEntryInfo`. `Open` returns a new reader over stored bytes or `os.ErrNotExist`.

State and persistence: in-memory map from normalized path to stat/data. `Add` mutates the caller-provided stat pointer.

Dependencies and integration: implements `fsutil.FS` for tests and static content injection.

Risks: `Walk` prefix matching is string-based and does not enforce path component boundaries. No directories are synthesized; only added files are walked. Not concurrency-safe.

Test signals: `static_test.go` covers add/open/read/not-found/walk order and metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static.go -->
