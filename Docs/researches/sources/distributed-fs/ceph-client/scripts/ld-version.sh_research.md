# sources/distributed-fs/ceph-client/scripts/ld-version.sh

## Purpose
`ld-version.sh` identifies the linker implementation and verifies it meets the minimum kernel build version, printing a canonical name and numeric version.

## Important APIs, Types, and Functions
`get_canonical_version()` converts `x.y.z` to `10000*x + 100*y + z`. The script recognizes GNU ld as `BFD`, rejects GNU gold, and recognizes LLVM LLD as `LLD`. It calls `scripts/min-tool-version.sh` for minimum `binutils` or `llvm` versions.

## Control Flow
With `set -e`, the script captures the first line of `$@ --version`, tokenizes it, selects the linker family, strips non-version suffixes, canonicalizes detected and minimum versions, fails if too old, and prints `BFD <version>` or `LLD <version>`.

## State and Persistence
No persistent state; output is stdout and diagnostics are stderr.

## Dependencies and Integration Points
Called by Kbuild host/toolchain checks. Depends on shell arithmetic, the linker executable passed as arguments, and `min-tool-version.sh`.

## Risks and Edge Cases
Version parsing assumes recognizable first-line formats. Gold is explicitly unsupported. Distribution suffixes are stripped after digits/dots. The `[` expressions use `-a`, which is portable enough for `/bin/sh` here but can be brittle with unusual tokens.

## Test Signals
Test with GNU ld, gold, LLD, unknown commands, old-version mocks, and version strings with package suffixes.
