# sources/distributed-fs/orangefs/src/client/windows/client-test/info.h

## Purpose
`info.h` declares metadata and volume-space tests for the client test runner.

## Important APIs, Types, And Functions
It declares `file_time(global_options *options, int fatal)` and `volume_space(global_options *options, int fatal)`.

## Control Flow
The functions are registered from `test-list.h` and run by `client-test.c` using the common test signature.

## State And Persistence
No state is declared in the header. Implementations create at most temporary test files.

## Dependencies And Integration Points
It includes `test-support.h`. The tests connect to Dokany metadata and statfs callbacks through standard library calls.

## Risks And Test Signals
As with other test headers, expected platform behavior and fatal policy are not represented here; they are split across implementation and `test-list.h`.
