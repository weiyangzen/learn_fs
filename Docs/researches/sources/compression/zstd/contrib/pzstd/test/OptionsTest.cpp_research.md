<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp -->
# sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp

## Purpose
This GoogleTest file verifies pzstd command-line parsing and output-file derivation.

## Important APIs, Types, And Functions
It defines equality helpers for `Options`, argument-vector helpers, expectation macros, and tests for valid inputs, output naming, multiple files, thread parsing, compression levels, unsupported/invalid options, keep/remove behavior, verbosity, test mode, checksum flags, stdin/stdout, and help/version messages.

## Control Flow
Each test constructs argv-like arrays, calls `Options::parse`, and compares the resulting `Options` fields or expected failure/message status.

## State And Persistence
State is local test data. It may inspect platform null-output naming but does not write files.

## Dependencies And Integration Points
It depends on GoogleTest, `Options.h`, and platform null-device conventions. It guards the behavior used by `main.cpp`.

## Risks
Tests mock argv behavior but do not fully cover console detection or recursive filesystem expansion.

## Test Signals
These tests are the primary regression signal for pzstd CLI compatibility and validation rules.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp -->
