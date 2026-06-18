# sources/compression/zstd/tests/regression/test.c

Purpose: This is the command-line regression runner. It parses required cache/output/zstd options plus optional filters and diff baseline, initializes data, runs every method/data/config tuple, writes a CSV-like compressed-size table, and optionally compares it to a prior result file.

Important APIs and functions: Globals store parsed options: `g_output`, `g_diff`, `g_cache`, `g_zstdcli`, `g_config`, `g_data`, and `g_method`. `is_name_bad()` and `are_names_bad()` reject NULL names, comma-containing names, and track maximum padding length. `parse_args()` uses `getopt_long()`. `tprintf()` and `tflush()` mirror result output to file and stderr. `run_all()` performs the matrix iteration. `diff_results()` loads two files with `data_buffer_read()` and compares them.

Control flow: `main()` parses arguments, validates names, sets the CLI path, initializes the data cache, opens the output file, calls `run_all()`, closes output, optionally diffs, then calls `data_finish()`. `run_all()` prints a header, iterates methods with optional method filter, iterates datasets with optional data filter, creates method state once per dataset, iterates configs with optional config filter, applies `config_skip_data()`, calls the method, suppresses skip results, and prints either an error string or compressed size.

State and persistence: The output results file is persistent and may be compared to a baseline. The data cache persists through `data_init()`. Global option pointers reference `argv` memory. `g_max_name_len` is computed during validation and used for aligned output.

Dependencies and integration points: Includes `config.h`, `data.h`, and `method.h`. Runtime requires a working zstd CLI path, writable output path, and cache directory. It is built by the regression Makefile.

Risks and test signals: `parse_args()` does not detect unknown trailing positional arguments. If `methods[method]->create()` returns NULL, some method implementations report system errors while others may rely on destroy tolerating NULL. The output is not strict CSV because fields are padded with spaces, but comma-free name validation keeps simple diffing stable. Success is exit code zero, a complete result table, and optional "actual results match expected results".
