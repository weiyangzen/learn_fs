# sources/compression/lz4/tests/test-lz4-versions.py

## Purpose
This Python harness validates file-format interoperability across historical `lz4c` and `lz4c32` releases. It builds each tagged command, compresses a reference file at multiple levels and word sizes, deduplicates equivalent compressed outputs, then decompresses every remaining artifact with every built decoder.

## Important APIs and Control Flow
`env_or_empty()`, `proc()`, `make()`, `git()`, `get_git_tags()`, and `sha1_of_file()` wrap environment-sensitive builds, command execution, tag discovery, and content hashing. Main flow clones upstream into `tests/versionsTest/lz4`, copies `README.md` as `test_dat`, builds `lz4c` and `lz4c32` for old `rNNN` and `vX.Y.Z` tags plus current head, creates compressed files, removes duplicates with `filecmp.cmp`, then verifies all decompressed files match `test_dat`.

## State, Dependencies, and Integration
Persistent state lives in `tests/versionsTest`, including built binaries, compressed samples, and decompressed outputs. Dependencies are `git`, `make`, working C compilers for 32-bit/64-bit variants, and historical source buildability. It integrates with the CLI file format and older command names.

## Risks and Test Signals
This is very strong backward/forward compatibility coverage, but expensive and network-dependent on first run. It assumes old tags build on the current host and that lexical tag collection is suitable. It exits on subprocess failure and cleans only selected generated outputs.
