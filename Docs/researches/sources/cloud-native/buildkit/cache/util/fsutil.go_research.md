# sources/cloud-native/buildkit/cache/util/fsutil.go

## Purpose

This file provides filesystem helper functions for reading, listing, and statting files under a cache/reference root while preserving user-facing request paths in errors.

## Important APIs, Types, and Functions

- `ReadRequest` and `FileRange` describe a file read and optional byte range.
- `ReadFile` resolves a path under a root, opens it, optionally applies an `io.SectionReader`, and returns all bytes.
- `ReadDirRequest` describes a directory listing request and optional include pattern.
- `ReadDir` walks one level of a resolved directory and returns fsutil stat entries.
- `StatFile` resolves and stats one path.
- `replaceErrorPath` rewrites an `os.PathError` path inside an error chain for clearer client errors.

## Control Flow and State

All public helpers first use `fs.RootPath` to resolve the requested path safely under the root. `ReadFile` rewrites open errors so internal root paths are replaced with the request filename, then reads either the full file or the requested section. `ReadDir` builds a `fsutil.FilterOpt`, walks the resolved path, appends `*fstypes.Stat` from each entry, and skips descending into directories beyond the current level. `StatFile` wraps `fsutil.Stat` and rewrites path errors using `replaceErrorPath`.

No persistent state is created. The functions read filesystem state only.

## Dependencies and Integration Points

The helpers depend on containerd continuity `fs.RootPath`, `tonistiigi/fsutil` stat/walk types, and BuildKit callers that expose gateway or cache reference filesystem operations. They are related to gateway `ReadFile`, `ReadDir`, and `StatFile` flows exercised in client tests.

## Risks and Edge Cases

`FileRange` uses `int`, then converts to `int64`; negative offsets or lengths are not explicitly validated here and rely on `io.NewSectionReader` behavior. `ReadDir` expects every walked `FileInfo.Sys()` to be `*fstypes.Stat`, returning an error otherwise. `replaceErrorPath` mutates an error object in place, and comments acknowledge that wrapped error strings may not always update if library behavior changes.

## Test Signals

`fsutil_test.go` verifies that rewriting an `os.PathError` returned by `fsutil.Stat` changes the rendered error string. There are no direct tests here for `ReadFile`, ranged reads, `ReadDir`, or root path escape behavior.
