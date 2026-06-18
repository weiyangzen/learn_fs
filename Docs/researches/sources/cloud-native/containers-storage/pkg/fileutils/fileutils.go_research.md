## sources/cloud-native/containers-storage/pkg/fileutils/fileutils.go

Purpose: file utility package for ignore-style pattern matching, file copying, symlink canonicalization, and create-if-missing helpers.

Important APIs/types/functions: `PatternMatcher`, `NewPatternMatcher`, `Matches`, `MatchesResult`, `IsMatch`, `Pattern`, `Pattern.compile`, package-level `Matches`, `CopyFile`, `ReadSymlinkedDirectory`, `ReadSymlinkedPath`, and `CreateIfNotExists`.

Control flow: patterns are trimmed, cleaned, marked as exclusions on `!`, syntax-checked with `filepath.Match`, lazily compiled to regex with special `**` handling, and evaluated in order where later matches override earlier state. Copying cleans paths, no-ops on identical clean path, removes existing destination, creates new destination, and streams bytes. Symlink readers resolve absolute paths through `EvalSymlinks`; directory variant rejects non-directories. `CreateIfNotExists` creates dirs recursively or parent dirs plus a file.

State and persistence: pattern regexes are cached in `Pattern.regexp` and are not concurrency-safe. `CopyFile` and `CreateIfNotExists` mutate the filesystem; symlink functions read filesystem metadata.

Dependencies and integration points: used by idtools and broader storage code for pattern exclusion and basic file operations. Depends on `logrus` for debug messages.

Risks: matcher methods are documented non-concurrent because lazy regex caching mutates patterns. `CreateIfNotExists` silently returns nil for non-NotExist errors from `Exists`, which can hide permission errors. Copy removes destination before ensuring creation succeeds.

Test signals: `fileutils_test.go` has extensive pattern matrix coverage plus copy, symlink-directory, and create-if-missing tests. Local execution blocked by missing `go`.
