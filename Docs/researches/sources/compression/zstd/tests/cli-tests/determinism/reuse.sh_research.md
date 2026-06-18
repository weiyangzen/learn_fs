# sources/compression/zstd/tests/cli-tests/determinism/reuse.sh

## Purpose
This test ensures compression context reuse across multiple input files does not affect deterministic output.

## APIs, control flow, and integration
It creates four data files of different sizes, defines `validate()` to compare each generated `.zst` with a `.good` reference, and loops levels 1 through 19. For each level it creates independent single-file references, then compresses the four files together in several different orders with `--single-thread`, validating that each output matches its reference.

## State, dependencies, risks, and test signals
State consists of generated inputs and `.zst`/`.good` outputs. Dependencies are `datagen`, `$DIFF`, deterministic build behavior, and exact stdout expectations. The risk is high sensitivity to any intentional change in context reuse or output naming. Pass indicates per-file compression results are invariant to prior files compressed by the same CLI invocation.
