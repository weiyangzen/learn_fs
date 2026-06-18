# sources/compression/zstd/tests/regression/result.h

Purpose: This header defines the result value used by regression methods. It carries either a successful compressed-size measurement or a typed error/skip result.

Important APIs and types: `result_error_t` enumerates ok, skip, system error, compression error, decompression error, and round-trip error. `result_data_t` contains `total_size`. `result_t` stores an internal error code and internal data. Static helper functions construct errors and data, test whether a result is error or skip, fetch the error, and fetch data. `result_get_error_string()` is implemented in `result.c`.

Control flow: Method implementations return `result_data()` on success, `result_error(result_error_skip)` for intentionally unsupported combinations, or another error for failures. `test.c` suppresses skips, prints error strings for errors, and prints `total_size` for successes.

State and persistence: Result values are passed by value and have no ownership or persistence.

Dependencies and integration points: Uses `stddef.h` for `size_t`. It is included by `method.h`, `method.c`, `result.c`, and `test.c`.

Risks and test signals: The header says not to access internal members directly, but the members are public in C and can be misused. `result_get_data()` does not assert non-error state, so callers must check first. Stable output depends on preserving enum/string meaning.
