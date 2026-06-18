<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/walk.go

Purpose: lexicographic filesystem walking and resumable path streaming that matches BadgerDB key ordering, including glob support and optional filtering.

Important APIs/types/functions: `WalkOptions`, `WalkOption`, `Lexicographically`, `WalkDirLexicographically`, `walkDirLexicographically`, `StreamPathResult`, `StreamPathsLexicographically`, `StreamPathsLexicographicallyWithDirs`, `streamPathsLexicographically`, `readDir`, `IsGlobPattern`, and `StripGlobPattern`.

Control flow: lexicographic walking recursively reads directories sorted by a custom name that appends `/` to directory names. Streaming normalizes `pattern` and `startAfter`, detects globs, expands glob directory patterns with `/**`, handles single-file patterns directly, finds a non-glob root, then launches a goroutine that walks sorted directories. It emits paths until `maxPaths` is reached, at which point it sends a resume token. Filtering is applied with `ApplyFilter`; directories may be emitted when `includeDirs` is true but are traversed even when not emitted.

State and persistence: no persistence; uses channel output and local `maxPaths` countdown. Reads filesystem directory contents and stat metadata.

Dependencies and integration points: depends on `doublestar` for glob matching, provider `Lstat/GetMountPath`, and filter helpers. `fs.go` uses `WalkDirLexicographically` when provider walk options request it. `walk_test.go` verifies ordering against `kvstore.MapStore`/Badger ordering.

Risks: walking runs in a goroutine; consumers must drain or cancel to avoid blocked sends. `maxPaths` is mutated inside the goroutine. Glob root discovery walks upward until an existing path but could behave unexpectedly for patterns rooted at missing trees. `readDir` filtering depends on string ordering with directory slash suffixes.

Test signals: `walk_test.go` covers custom walk order, Badger order comparison, glob patterns, resume behavior, max-path resume tokens, and deeply nested matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk.go -->
