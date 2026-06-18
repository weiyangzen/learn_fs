# sources/distributed-fs/juicefs/pkg/object/prefix_test.go

Purpose: validates parent-directory derivation for object storages that may represent either a directory root or a file-like target.

Important APIs and types: `TestDirStorage` creates an in-memory base store with `CreateStorage("mem", ...)`, builds table-driven `ObjectStorage` instances using `WithPrefix` and `filestore`, and checks resulting `String()` values after `DirStorage`.

Control flow and state: each case constructs a fresh storage, calls `DirStorage`, and compares display strings. Covered cases include an already-directory prefix, a nested file prefix, a top-level file prefix, an empty prefix, and filestore directory/file roots.

Persistence and integration: the test does not write objects; it exercises path normalization and wrapper unwrapping behavior at the object layer. It depends on the memory and file store registrations being available in the test package.

Risks and test signals: this test is focused and catches regressions in prefix cleanup such as returning `./`, losing trailing slashes, or failing to unwrap top-level file prefixes. It does not cover encrypted wrappers, copy prefix semantics, list key rewriting, or optional interface passthroughs.
