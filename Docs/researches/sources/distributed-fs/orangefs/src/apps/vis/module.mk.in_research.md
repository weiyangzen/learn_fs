<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/vis/module.mk.in

## Purpose
Build-system fragment for optional OrangeFS visualization tools.

## Important APIs, Types, And Functions
When `BUILD_VIS` is set, it adds `simple.c` and `pvfs2-vis-bw-2d.c` to `VISSRC`, adds `pvfs2-vis.c` to `VISMISCSRC`, and injects configured SDL compiler/linker flags plus `-lSDL_ttf`.

## Control Flow
The entire block is conditional on `BUILD_VIS`. This separates SDL-dependent tools from default builds.

## State And Persistence
No runtime state. Build-time state is CFLAGS/LDFLAGS and source-list membership.

## Dependencies And Integration Points
Depends on configure substitutions `@VISCFLAGS@` and `@VISLIBS@` and top-level make rules that build visualization binaries from `VISSRC` and shared misc sources.

## Risks And Test Signals
Risks include SDL/SDL_ttf detection drift, missing `pvfs2-vis.h` as a dependency if headers are tracked separately, and link-order issues because common source is in `VISMISCSRC`. Test signals are configure/build with visualization enabled/disabled and running linked tools against an OrangeFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/module.mk.in -->
