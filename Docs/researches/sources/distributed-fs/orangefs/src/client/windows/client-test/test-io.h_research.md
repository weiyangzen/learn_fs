# sources/distributed-fs/orangefs/src/client/windows/client-test/test-io.h

## Purpose
`test-io.h` declares IO-related tests for the client test runner.

## Important APIs, Types, And Functions
It declares `io_file`, `flush_file`, and `io_file_mt`, all using the shared `global_options`/`fatal` signature.

## Control Flow
`test-list.h` registers these functions, and `client-test.c` invokes them either in the default suite or by explicit test name.

## State And Persistence
The header has no state. Implementations create temporary files and directories under the configured root.

## Dependencies And Integration Points
It includes `test-support.h`. Tests exercise mounted OrangeFS IO through the C runtime and, under the service, the Dokany read/write/flush callbacks.

## Risks And Test Signals
The header does not expose test sizes, thread counts, or performance semantics, so changing those in `test-io.c` can significantly alter runtime without any declaration change.
