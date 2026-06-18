# sources/cloud-native/containers-storage/pkg/system/stat_freebsd_test.go

Purpose: FreeBSD tests for `fromStatT` and file flag reporting.

Important APIs/types/functions: `platformTestFromStatT` compares mode and mtime; `TestFileFlags` writes a file, sets `UF_READONLY` with `Lchflags`, and checks `Stat(file).Flags()`.

Control flow: creates temporary files, applies flags, reads stat metadata, and uses fatal assertions on mismatch.

State/persistence: mutates temporary file flags and relies on cleanup of temp directories.

Dependencies/integration: exercises FreeBSD `Lchflags`, `Stat`, and `StatT.Flags`.

Risks: requires filesystem support and permissions for `chflags`; failures may be environmental rather than logical.

Test signals: strong platform signal that FreeBSD-specific flag plumbing remains wired into stat and removal support.
