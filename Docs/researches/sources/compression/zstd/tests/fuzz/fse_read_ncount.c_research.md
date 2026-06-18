# sources/compression/zstd/tests/fuzz/fse_read_ncount.c

## Purpose
This fuzz target round-trips FSE normalized-count serialization and parsing.

## APIs, control flow, and state
`LLVMFuzzerTestOneInput()` chooses `tableLog` and `maxSymbolValue`, fills a `short ncount[256]` distribution whose normalized weights sum to `1 << tableLog`, writes it with `FSE_writeNCount()`, appends a fuzz-selected amount of random trailing bytes, reads it back with `FSE_readNCount()`, and asserts the consumed byte count, max symbol value, table log, and all normalized counts match the original.

## Dependencies, risks, and test signals
Dependencies are static FSE APIs, zstd helper assertions, and `fuzz_data_producer` for parameter selection. The key risk is that generated distributions must maintain FSE invariants; otherwise the target would test writer precondition failures rather than reader correctness. The signal is exact read/write equality with sanitizer/assertion cleanliness.
