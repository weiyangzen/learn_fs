# sources/compression/zstd/tests/datagencli.c

## Purpose
`datagencli.c` implements the standalone `datagen` test utility. It generates deterministic synthetic data to stdout for zstd tests, either lorem-style text or randomized data with a requested compressibility.

## APIs, functions, and control flow
The executable has `usage()` and `main()`. `main()` parses aggregated short options: `-g#` size with optional `K`, `M`, `G`, `B`; `-s#` seed; `-P#` compressibility percent clamped to 100; hidden `-L#` literal distribution probability; `-v`; and `-h`. If `-P` is supplied it calls `RDG_genStdout(size, proba, litProba, seed)`, otherwise it calls `LOREM_genOut(size, seed)`.

## State, dependencies, integration, and risks
There is no persisted state; output is written to stdout and diagnostics to stderr depending on `displayLevel`. Dependencies are `datagen.h`, `loremOut.h`, and `util.h` types. It is integrated throughout CLI tests and corpus generation scripts. Risks include permissive numeric parsing without invalid suffix diagnostics, overflow in very large sizes, and hidden `-L` behavior being coupled to tests without help output.

## Test signals
Downstream tests use `datagen` success, deterministic seed behavior, and output size/compressibility as setup signals. Failures usually surface as bad test fixtures rather than direct unit assertions in this file.
