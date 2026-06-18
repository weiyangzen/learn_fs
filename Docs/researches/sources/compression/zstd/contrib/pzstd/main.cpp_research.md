<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/main.cpp -->
# sources/compression/zstd/contrib/pzstd/main.cpp

## Purpose
`main.cpp` is the pzstd executable entry point.

## Important APIs, Types, And Functions
It defines `main(int argc, const char** argv)`, constructs `Options`, invokes `Options::parse`, and on success calls `pzstdMain`.

## Control Flow
If parsing returns `Failure`, it exits nonzero. If parsing returns `Message` for help/version, it exits zero without running compression. Otherwise it delegates to the engine and returns its status.

## State And Persistence
The entry point owns only the stack `Options` object. Persistent effects are produced by `pzstdMain`.

## Dependencies And Integration Points
It includes `Options.h` and `Pzstd.h`, tying CLI parsing to the pzstd engine.

## Risks
Exit-code semantics depend on `Options::Status`; changes to parse status mapping directly affect scripts invoking pzstd.

## Test Signals
`OptionsTest.cpp` validates parse statuses; round-trip tests exercise the engine beneath this entry point.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/main.cpp -->
