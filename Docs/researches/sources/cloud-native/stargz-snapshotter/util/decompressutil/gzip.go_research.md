<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go -->
# sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go

## Purpose
Selects a gzip decompression helper for eStargz, preferring external commands when configured and available with fallback to Go's standard gzip reader.

## Important APIs, Types, And Functions
- Package globals cache discovered paths for `gzip`, `pigz`, and `igzip` behind `sync.Once`.
- `GetGzipHelperFunc(gzipHelper)` validates helper name and returns an `estargz.GzipHelperFunc`.
- `getCmdGzipHelperFunc` runs `<cmd> -d -c` with stdin/stdout pipes.
- `getGoGzipHelperFunc` wraps `gzip.NewReader`.
- `findCmdPath` uses `exec.LookPath`.

## Control Flow
On first use, command paths are discovered. The requested helper name selects a cached path; missing paths print a warning and use Go gzip, invalid names return an error. External helpers start a subprocess and report wait/stderr failures through the pipe.

## State And Persistence
Only in-memory command path cache is retained. No files are written.

## Dependencies And Integration Points
Used by eStargz decompression configuration. Depends on host binaries for parallel/accelerated decompression when available.

## Risks And Edge Cases
Command discovery is one-time unless tests reset `sync.Once`. External helper failures surface while reading, not at helper creation. Warning uses stdout, which can be noisy in libraries.

## Test Signals
Tests cover invalid helper errors, available command decompression, fallback to Go gzip when missing, and exact decompressed bytes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip.go -->
