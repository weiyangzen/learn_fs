# sources/compression/xz/src/liblzma/validate_map.sh

## Purpose
Shell validation script for liblzma symbol version map files. It detects missing exported API symbols, obsolete alpha/beta version names, duplicate map lines, and divergence between generic and Linux maps.

## Important APIs, Types, And Functions
No functions are defined. Important variables:
- `SYMS` lists API symbols from `api/lzma/*.h` that are absent from `liblzma_generic.map`.
- `VER` and `NAMES` check alpha/beta version naming.
- `DUPS` identifies duplicate map lines.
- `IN_SYNC` flags mismatch between `liblzma_linux.map` and `liblzma_generic.map` after deleting fixed compatibility lines.
- `STATUS` is final exit status.

## Control Flow
The script sets `LC_ALL=C`, changes to its own directory, derives missing symbols with `sed`, `sort`, and `grep`, obtains package version via `build-aux/version.sh`, checks old alpha/beta names for non-development releases, finds duplicate map lines, compares Linux and generic maps with a fixed line deletion, prints grouped diagnostics if anything is wrong, and exits 1 on problems or 0 otherwise.

## State And Persistence
No persistent state. It reads source headers and map files and writes diagnostics to stdout.

## Dependencies And Integration Points
Depends on POSIX shell, `sed`, `sort`, `grep`, `cmp`, and `build-aux/version.sh`. Intended for maintainer/build validation around `liblzma_generic.map` and `liblzma_linux.map`.

## Risks
Line-number deletion `sed '111,125d'` is brittle if the Linux compatibility block moves. Symbol extraction regex only matches a specific `extern LZMA_API(...) name(` pattern. Map parsing ignores lines containing `{}`, `:`, or `*`, so formatting changes can affect results.

## Test Signals
Run in CI/maintainer checks. Mutating maps to remove a symbol, add duplicate lines, or desynchronize Linux/generic maps should produce expected failures.
