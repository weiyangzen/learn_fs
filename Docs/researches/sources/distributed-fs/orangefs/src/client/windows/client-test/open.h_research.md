# sources/distributed-fs/orangefs/src/client/windows/client-test/open.h

## Purpose
`open.h` declares the basic open-mode test.

## Important APIs, Types, And Functions
It declares `open_file(global_options *options, int fatal)`.

## Control Flow
The function is registered in `test-list.h` and called through the generic test runner.

## State And Persistence
The header has no state. `open.c` manages temporary file creation and cleanup.

## Dependencies And Integration Points
It includes `test-support.h`. The declaration participates in the mounted-filesystem smoke-test suite.

## Risks And Test Signals
The copyright year differs from surrounding files, suggesting old code. The single declaration gives no detail about tested modes; callers must consult `open.c`.
