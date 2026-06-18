# sources/distributed-fs/ipfs-kubo/Makefile

## Purpose
This small wrapper delegates ordinary `make` invocations to GNU Make.

## Important APIs, Types, And Functions
It defines `all` and `.DEFAULT` targets that execute `gmake $@`.

## Control Flow
Any target requested through `make` is handed to `gmake`, which then loads `GNUmakefile`/`Rules.mk`.

## State And Persistence Behavior
It creates no state directly.

## Dependencies And Integration Points
It assumes `gmake` exists and is the intended build engine.

## Risks And Test Signals
Risks are missing `gmake` or recursive make edge cases. Signal is `make build`, `make test`, and other targets dispatching to GNU Make successfully.
