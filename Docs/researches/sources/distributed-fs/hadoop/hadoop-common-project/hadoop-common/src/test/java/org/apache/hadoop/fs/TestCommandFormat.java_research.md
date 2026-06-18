# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestCommandFormat.java

## Purpose
`TestCommandFormat` unit-tests Hadoop shell command-line parsing in `CommandFormat`. It verifies minimum and maximum argument counts, unknown-option rejection, option collection, `--` option-stop handling, dash-as-argument handling, and old array parsing with a start index.

## Important APIs, Types, And Functions
The fixture uses static `args`, `expectedArgs`, and `expectedOpts`, reset before each test. `checkArgLimits()` constructs `CommandFormat`, parses a copy of `args`, records any `IllegalArgumentException`, and compares the error class, remaining arguments, and collected options. Helpers `listOf()` and `setOf()` build expected collections. It imports `NotEnoughArgumentsException`, `TooManyArgumentsException`, and `UnknownOptionException`.

## Control Flow
Tests set up a specific token list and expected parse results, then call `checkArgLimits()` with several min/max/option combinations. `testArgOpt()` demonstrates that option parsing stops once a non-option argument is encountered. `testOptStopOptArg()` verifies `--` stops option parsing and keeps following `-b` as an argument. `testOptDashArg()` treats single `-` as an argument. `testOldArgsWithIndex()` parses a string array from different offsets.

## State And Persistence Behavior
There is no persistence. Static fixture lists are reassigned before each test.

## Dependencies And Integration Points
The parser is used by Hadoop filesystem shell commands. These tests protect command implementations that rely on parsed option sets and positional argument lists.

## Risks
The shared static fixture is safe under normal JUnit execution with per-test reset but would be fragile under concurrent test-method execution. Tests compare exact exception classes but not messages, except messages are printed to stdout during failures.

## Test Signals
Passing tests show `CommandFormat` enforces arity, recognizes configured options, rejects unknown options, preserves argument ordering after parsing, and supports legacy array parsing offsets.
