# sources/distributed-fs/ipfs-kubo/GNUmakefile

## Purpose
This wrapper makes GNU Make behavior available when the user invokes `gmake`.

## Important APIs, Types, And Functions
It sets `SHELL`, enables `.SECONDEXPANSION`, includes `Rules.mk`, and defines `all` plus `.DEFAULT` to delegate to `gmake`.

## Control Flow
Targets flow into the common Make rule graph in `Rules.mk`.

## State And Persistence Behavior
It only influences build invocation state; generated files are owned by included rules.

## Dependencies And Integration Points
It integrates with GNU Make and all included `mk/*.mk` fragments.

## Risks And Test Signals
Risks are recursive/delegation confusion on systems where `make` and `gmake` differ. Signal is standard targets resolving through `Rules.mk`.
