<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.cpp -->
# sources/compression/zstd/contrib/pzstd/Options.cpp

## Purpose
`Options.cpp` parses pzstd command-line arguments and turns zstd-like CLI options into an `Options` configuration.

## Important APIs, Types, And Functions
Important helpers are `defaultNumThreads`, `parseUnsigned`, `getArgument`, `notSupported`, `usage`, `Options::Options`, `Options::parse`, and `Options::getOutputFile`.

## Control Flow
Parsing scans argv, maps long options to short options, handles combined short options and numeric compression levels, validates multi-file/stdin/output restrictions, expands recursive file lists when enabled, rejects unsupported dictionaries/benchmarks/sparse mode, checks console safety, and adjusts verbosity for pipe/multi-file modes.

## State And Persistence
It mutates an `Options` instance: thread count, compression level, mode flags, input files, output file, checksum flag, and verbosity. It also sets `g_utilDisplayLevel` for zstd utility code.

## Dependencies And Integration Points
It depends on zstd static APIs, `util.h` for file traversal/link checks, console macros, and `ScopeGuard`. `main.cpp` calls it before `pzstdMain`.

## Risks
CLI compatibility is partial; unsupported zstd options fail. Symlink filtering and recursive expansion depend on platform utility behavior. Console-safety checks can differ across environments.

## Test Signals
`OptionsTest.cpp` broadly covers valid inputs, bad arguments, output naming, multi-file restrictions, verbosity, keep/remove, test mode, checksum, stdin/stdout, and message options.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.cpp -->
