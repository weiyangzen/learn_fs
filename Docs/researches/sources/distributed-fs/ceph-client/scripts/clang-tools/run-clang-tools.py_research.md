# sources/distributed-fs/ceph-client/scripts/clang-tools/run-clang-tools.py

## Purpose
`run-clang-tools.py` runs `clang-tidy` over every C/C++ entry in a compilation database, selecting either Linux kernel tidy checks or clang static analyzer checks.

## Important APIs, Types, and Functions
`parse_arguments()` accepts `clang-tidy` or `clang-analyzer`, the compilation database path, optional `-checks`, and optional `-header-filter`. `init()` shares a multiprocessing lock and parsed args with workers. `run_analysis()` builds the `clang-tidy` invocation, skips non-C/C++ files, runs in the entry directory, and serializes output through the lock.

## Control Flow and State
`main()` creates a multiprocessing pool, loads JSON from the database, and maps each entry to `run_analysis()`. Default checks are `linuxkernel-*` for tidy and `clang-analyzer-*` with one insecure API checker disabled for analyzer mode. There is no persistent state.

## Dependencies and Integration
It depends on Python 3, a valid `compile_commands.json`, multiprocessing, and `clang-tidy` in `PATH`. It is intended to consume the database produced by `gen_compile_commands.py`.

## Risks and Test Signals
The BrokenPipeError handler references `os` without importing it, so EPIPE cleanup can raise a secondary error. Analyzer mode still invokes `clang-tidy`; the mode only changes check names. Test with mixed `.c`, `.cpp`, and assembly entries, custom check lists, header filters, missing tools, malformed JSON, and piped output closed early.
