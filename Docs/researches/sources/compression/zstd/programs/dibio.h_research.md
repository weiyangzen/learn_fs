# sources/compression/zstd/programs/dibio.h

## Purpose
`dibio.h` declares the zstd program dictionary-training file I/O API. Its own comment makes clear it is designed for a single-threaded console application and may call `exit()` or print to stderr on errors.

## Important APIs, types, and functions
The sole public function is `DiB_trainFromFiles()`. It accepts an output dictionary path, maximum dictionary size, an input file-name table, file count, optional chunk size, one of the zdict parameter families, an optimize flag, and a memory limit. The function returns zero for success and nonzero for error when errors are recoverable through the implementation path.

## Control flow
The header does not implement control flow. It exposes one high-level operation that hides sample loading, memory limiting, zdict training-family selection, and dictionary saving behind a single call.

## State and persistence behavior
The API writes a dictionary file named by `dictFileName`. Based on the implementation contract, it may also mutate the input file-name table order and may terminate the process on fatal errors. No reusable context object or persistent handle is declared.

## Dependencies and integration points
The header defines `ZDICT_STATIC_LINKING_ONLY` and includes `../lib/zdict.h` for `ZDICT_legacy_params_t`, `ZDICT_cover_params_t`, and `ZDICT_fastCover_params_t`. It is integrated into the zstd CLI dictionary builder rather than a general-purpose library API.

## Risks and edge cases
Because it exposes raw pointer tables and mutable parameter structs, callers must ensure all pointers remain valid for the full call and that exactly one parameter family is selected. The console-app error behavior makes it risky for embedders that require non-fatal error reporting.

## Test signals
Compile coverage should validate callers can include the header with zdict static APIs. Integration tests should call `DiB_trainFromFiles()` with each parameter family and verify output dictionary creation, error behavior for too few samples, and memory-limit handling.
