<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in

## Purpose
Registers the user-cache daemon sources in the OrangeFS build when `BUILD_UCACHE` is enabled.

## Important APIs, Types, And Functions
The make fragment sets `DIR := src/apps/ucache` and appends `ucached.c` and `ucached_cmd.c` to `UCACHEDSRC`. There are no functions; the API is the build variable contract consumed by higher-level make logic.

## Control Flow
The whole fragment is gated by `ifdef BUILD_UCACHE`; when unset it contributes no sources. When set, both daemon and command helper are compiled as the user-cache application set.

## State And Persistence
No runtime state. Build state is the make variable expansion used during configure-generated builds.

## Dependencies And Integration Points
Depends on the top-level make system defining `BUILD_UCACHE` and consuming `UCACHEDSRC`. It ties the application layer to user-cache shared-memory support under `src/client/usrint`.

## Risks And Test Signals
Risks are stale source lists if ucache files move or new daemon support files are added without updating this fragment. Test signals are configure/build runs with `BUILD_UCACHE` enabled and disabled, verifying that both `ucached` and `ucached_cmd` targets are present only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/module.mk.in -->
