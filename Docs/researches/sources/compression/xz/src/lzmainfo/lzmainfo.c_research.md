# sources/compression/xz/src/lzmainfo/lzmainfo.c

## Purpose
Implements the `lzmainfo` command-line tool for compatibility with LZMA Utils, printing metadata from the 13-byte `.lzma` header.

## Important APIs, Types, And Functions
- `help()` prints localized usage and exits.
- `version()` prints package version and exits.
- `parse_args()` handles `--help` and `--version`.
- `my_log2()` computes a simple base-2 exponent for dictionary display.
- `lzmainfo()` reads and parses one file's header, prints uncompressed size, dictionary size, lc, lp, and pb.
- `main()` initializes program name/gettext, sets binary stdin on DOS-like systems, dispatches stdin/files, and exits via tuklib.

## Control Flow
`main()` parses options, then either reads stdin or loops over operands. For each file, `lzmainfo()` reads 13 bytes, decodes first five bytes with `lzma_properties_decode()` for LZMA1, interprets the next eight bytes as little-endian uncompressed size, prints fields in LZMA Utils-compatible text, frees decoded options, and reports errors without aborting the whole file loop except for memory/internal errors.

## State And Persistence
No persistent state besides process exit status. Each file allocates and frees `filter.options`.

## Dependencies And Integration Points
Depends on liblzma API, getopt, gettext/tuklib wrappers for program name, nonprint masking, wrapping, and exit. Built by `src/lzmainfo/Makefile.am`.

## Risks
It opens files with `"r"` rather than `"rb"` except stdin is set binary on DOS-like systems; platform C runtime behavior may matter. `my_log2()` assumes meaningful dictionary sizes from decoded properties. Output format is intentionally not translated in the data fields to preserve script compatibility.

## Test Signals
Run against valid `.lzma` headers with known/unknown uncompressed sizes, invalid property byte, too-short file, stdin, `-` operand, multiple files, nonprint filenames, and `--help`/`--version`.
