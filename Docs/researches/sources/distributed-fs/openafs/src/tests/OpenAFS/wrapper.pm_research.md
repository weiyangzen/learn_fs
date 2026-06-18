<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm

## Purpose
Implements the generic subprocess execution and line-oriented parsing engine used by the AFStools wrappers, plus a generated-code `fast_wrapper` variant.

## Important APIs, Types, And Functions
Exports `wrapper`; optionally exports `fast_wrapper`. `_fastwrap_gen` emits Perl code for a parsing instruction list. Parser actions support scalar, array, hash, code, result-key strings, stop-line `.`, skip `+n`, error `-`, and print `?`.

## Control Flow
`wrapper` combines built-in wrapper/command error patterns with caller parse instructions, resolves the executable path from `%AFScmd` unless overridden, forks with a pipe, redirects stderr/stdout according to options, execs the command, and applies every parsing instruction to each output line until EOF or an exception. `fast_wrapper` compiles equivalent parser code, forks similarly, and invokes the generated parser.

## State And Persistence
Uses dynamic local `%result` for parser output and reads `%AFS_Trace`/`%AFScmd`; it writes no persistent state. Side effects are entirely from the invoked child command and optional pass-through output.

## Dependencies And Integration Points
Depends on `OpenAFS::util`, `Exporter`, and `Symbol`. All `bos`, `fs`, `pts`, `vos`, and `kas` modules route command execution through it.

## Risks And Test Signals
The code often checks `%options` as `$options{...}` instead of `$options->{...}`, so `pass_stdout`/`pass_stderr` behavior may not match the supplied hash reference. `exec($path $cmd, @$args)` is unusual and risks argv/path bugs. Fast wrapper generation contains fragile emitted hash/code action logic. Signals are wrapper unit tests for stderr capture, stdout pass-through, parse actions, command-not-found, and generated parser parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/wrapper.pm -->
