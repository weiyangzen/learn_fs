<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in

## Purpose
Adds the token utility implementation to OrangeFS library and server builds.

## Important APIs, Types, And Functions
Sets `DIR := src/common/token-utils` and appends `$(DIR)/token-utils.c` to both `LIBSRC` and `SERVERSRC`.

## Control Flow
The build system includes `token-utils.c` in shared client/library code and server code.

## State And Persistence
No runtime state exists in this make fragment.

## Dependencies And Integration Points
Integrates `token-utils` with code that needs delimiter-based token iteration.

## Risks And Test Signals
Risks are duplicate object inclusion or missing linkage if parent makefiles handle `LIBSRC`/`SERVERSRC` unexpectedly. Full client and server builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/token-utils/module.mk.in -->
