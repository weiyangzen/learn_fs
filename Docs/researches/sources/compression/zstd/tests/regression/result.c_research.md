# sources/compression/zstd/tests/regression/result.c

Purpose: This tiny implementation maps `result_t` error codes to human-readable strings for regression output.

Important APIs and functions: It implements `result_get_error_string(result_t result)`, switching on `result_get_error()` and returning strings for ok, skip, system error, compression error, decompression error, round trip error, and unknown error.

Control flow: The function is a straightforward switch. It is called by `test.c` when a method returns an error result that is not skipped.

State and persistence: None. Returned string literals are static and immutable.

Dependencies and integration points: Depends only on `result.h`. Its strings become part of the regression result table and any diff baseline, so changes can affect expected outputs.

Risks and test signals: Adding a new `result_error_t` without updating this switch will produce "unknown error" in output. Correct behavior is visible as readable error labels in the CSV-like results table.
