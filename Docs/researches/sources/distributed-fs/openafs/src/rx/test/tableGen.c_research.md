# sources/distributed-fs/openafs/src/rx/test/tableGen.c

## Purpose
`tableGen.c` generates RPC signature tables for `generator.c`. It creates deterministic combinations of argument directions and types, plus additional randomized multi-argument signatures.

## Important APIs, Types, and Functions
- Global `dir`/`typ` arrays are populated from command-line lists or defaults.
- `drand32()` mirrors the deterministic RNG used by `generator.c`.
- `SingleArg()`, `DoubleArg()`, and `BunchArg()` emit one-line signatures.
- `ProcessCmdLine()` handles optional append input, output file, and direction/type overrides.

## Control Flow
The program parses arguments, opens the output file, optionally copies an append file into it, emits one single-argument signature per type, emits every two-type combination, then emits 100 randomized signatures of up to `MAX_ARGS` arguments.

## State and Persistence
Persistent state is the generated output table. Runtime state is the selected direction/type arrays and deterministic RNG seed. With identical options and append file, output is deterministic.

## Dependencies and Integration Points
The output format is explicitly coupled to `generator.c`: `argCount ( DIR TYPE ) ...`. Default types include scalar, string, and array names recognized by the generator.

## Risks and Edge Cases
Changing emitted format breaks `generator.c`. Command parsing manually walks argv and assumes value lists stop at the next `-` argument. It avoids `INOUT varString` because the generator cannot handle reference string pointers for those cases.

## Test Signals
A useful signal is that `generator.c -f <table>` can parse all emitted lines and produce rxgen-compatible output. Deterministic output diffs are also meaningful because the RNG seed is fixed.
