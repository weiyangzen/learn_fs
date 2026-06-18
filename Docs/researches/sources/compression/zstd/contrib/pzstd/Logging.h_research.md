<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Logging.h -->
# sources/compression/zstd/contrib/pzstd/Logging.h

## Purpose
`Logging.h` provides pzstd's verbosity-controlled stderr logging and progress-line update helper.

## Important APIs, Types, And Functions
It defines log levels such as error/info/verbose/debug and class `Logger` with `operator()`, `update`, `clear`, and `logsAt`.

## Control Flow
Callers construct a logger with the parsed verbosity. Normal logs emit formatted messages when the level is enabled; update/clear manage progress text by rewriting or clearing the active line.

## State And Persistence
State is the verbosity threshold and progress-line bookkeeping. Output is transient stderr text.

## Dependencies And Integration Points
`SharedState` owns a `Logger`, and `Pzstd.cpp` uses it for frame starts, progress, ratios, prompts, and errors.

## Risks
Progress updates can interleave with worker output if future code logs outside the main writer path. Format-string usage requires trusted static formats.

## Test Signals
Option tests validate verbosity parsing; runtime pzstd tests indirectly exercise logging without asserting exact stderr.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Logging.h -->
