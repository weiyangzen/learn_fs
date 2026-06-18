# sources/cloud-native/buildkit/cache/contenthash/path_test.go

Purpose: tests root-confined symlink resolution in `path.go`.

Important APIs/types/functions: `TestRootPathSymlinks`, `mkdirAll`, and `symlink`.

Control flow: constructs a synthetic directory tree with symlinks to targets, symlinks through other symlinks, absolute symlinks, parent-directory components, and a top-level link to a subtree. It runs table-driven subtests for `followTrailing=true` and false, comparing `rootPath` output to expected paths under the temp root.

State and persistence behavior: only temporary filesystem state. It validates no contenthash metadata directly.

Dependencies and integration points: uses standard testing/os/path/filepath/runtime and testify require. Windows helper prefixes absolute symlink targets with a dummy drive letter and skips if Windows normalizes targets in a way that invalidates Linux-compatibility expectations.

Risks: primarily validates behavior, not symlink-loop error paths. Some cases are skipped on Windows when symlink contents differ from requested targets.

Test signals: strong regression signal for `rootPath`, which is then used by `checksum.go` scan behavior.
