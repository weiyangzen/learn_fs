# sources/compression/lz4/tests/datagencli.c

## Purpose
`datagencli.c` is the command-line frontend for producing test data. With explicit compressibility it emits random LZ4-oriented data; otherwise it emits lorem ipsum text.

## Important APIs, Types, and Functions
`main()` parses options and dispatches to `RDG_genOut()` or `LOREM_genOut()`. `usage()` prints supported flags. Global `displayLevel` and `DISPLAYLEVEL` control stderr diagnostics. Supported options include `-g#` with K/M/G/B suffixes, `-s#`, `-P#`, hidden `-L#`, `-v`, and `-h`.

## Control Flow, State, and Persistence
Parsing supports aggregated short options and updates local `size`, `seed`, `proba`, and `litProba`. `COMPRESSIBILITY_NOT_SET` selects lorem output; otherwise `proba / 100.0` drives `RDG_genOut()`. The program streams generated data to stdout and writes diagnostics to stderr. No files are opened directly.

## Dependencies and Integration Points
It depends on `datagen.h`, `loremOut.h`, `lz4.h` for the version string, and `util.h` typedefs. It is a test utility entry point around the lower-level generators.

## Risks and Test Signals
Risks include minimal validation for malformed numeric suffixes, silent overflow when shifting very large sizes, and unchecked stdout write failures in the generator. Useful signals are deterministic `-s` output, CLI exit code `1` for unknown options, and fallback to lorem output when `-P` is omitted.
