## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_test.go

Purpose: comprehensive tests for copy helpers, symlink resolution, create-if-missing, and Docker/gitignore-like pattern matching.

Important APIs/types/functions: tests for `CopyFile`, `ReadSymlinkedDirectory`, `Matches`, `NewPatternMatcher`, `MatchesResult`, `CreateIfNotExists`, and helper tables `matchesTestCase`/`matchTests`.

Control flow: uses temp files for copy/create cases, fixed `/tmp` paths for symlink directory tests, and large table-driven pattern matrices for `*`, `**`, character classes, exclusions, malformed patterns, match counts, and platform-specific escaping.

State and persistence: creates and removes files, directories, and symlinks. Some symlink tests use hard-coded `/tmp` names rather than `t.TempDir`.

Dependencies and integration points: validates behavior needed by ignore/exclusion consumers and file operations in storage utilities.

Risks: hard-coded `/tmp` paths can collide with parallel runs or pre-existing files. Pattern tests rely on filepath behavior that differs on Windows and conditionally skip escape cases.

Test signals: strong for pattern semantics and basic copy/create helpers; no direct tests for `ReadSymlinkedPath`. Local execution unavailable because `go` is missing.
