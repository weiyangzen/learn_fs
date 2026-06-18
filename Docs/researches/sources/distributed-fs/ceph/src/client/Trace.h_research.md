# sources/distributed-fs/ceph/src/client/Trace.h

## Purpose
`Trace.h` declares the trace iterator used to replay synthetic operation traces.

## Important APIs, Types, and Functions
`Trace` owns `_line`, `filename`, an `ifstream*`, and current `line`. Public APIs are `start()`, `peek_string()`, `get_string()`, `get_int()`, `get_line()`, and `end()`. The destructor deletes the stream. Copy constructor and assignment are declared, indicating copy semantics are intentionally controlled.

## Control Flow
Callers construct with a filename, call `start()`, then repeatedly call `get_string()` or `get_int()` until `end()`. `peek_string()` allows inspecting the current token without advancing.

## State and Persistence Behavior
The object is a non-persistent cursor over a file. `end()` returns true when no stream exists or the stream is at EOF.

## Dependencies and Integration Points
It uses C++ streams, strings, lists, and `atoll()`. `SyntheticClient.cc` relies on one trace token per line and uses `get_int()` for numeric arguments.

## Risks
The raw `ifstream*` requires careful copy behavior. EOF and malformed integer handling are lenient; `atoll()` returns 0 for invalid strings.

## Test Signals
Trace replay tests should include token ordering, numeric conversion, EOF after final line, and prefix-expansion semantics.
