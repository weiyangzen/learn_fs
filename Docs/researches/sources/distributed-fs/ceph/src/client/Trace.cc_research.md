# sources/distributed-fs/ceph/src/client/Trace.cc

## Purpose
`Trace.cc` implements a simple line-oriented trace reader consumed by `SyntheticClient::play_trace()`.

## Important APIs, Types, and Functions
`Trace::start()` reopens the configured trace file and primes the first line. `Trace::peek_string()` returns the current line, optionally replacing a leading `/prefix` marker with the caller-provided prefix. `Trace::get_string()` returns the current token and advances to the next line. Integer reads are implemented inline in the header through `get_int()`.

## Control Flow
The reader keeps one current line buffered. `start()` deletes any previous stream, opens a new `ifstream`, aborts on failure, reads the first line, and sets `_line` to 1. Each `get_string()` calls `peek_string()`, increments `_line`, and performs `getline()` for the next token.

## State and Persistence Behavior
State is in-memory only: filename, stream pointer, current line, and line counter. It does not persist offsets between starts; every `start()` rewinds by reopening the file.

## Dependencies and Integration Points
It depends on `Trace.h`, Ceph debug/config headers, and C string helpers. Its `/prefix` expansion is coupled to synthetic trace path conventions.

## Risks
Failure to open aborts the process. The reader has no token validation, no explicit EOF error for missing arguments, and copy/assignment are declared but not implemented here, so accidental use would need definitions elsewhere or cause link errors.

## Test Signals
Tests should cover open failure, line number increments, EOF behavior, and `/prefix` substitution with empty and non-empty prefixes.
