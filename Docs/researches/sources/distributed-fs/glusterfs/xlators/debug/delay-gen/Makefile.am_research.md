# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/Makefile.am

## Purpose
This Automake file delegates the delay-gen debug translator build to its `src` directory.

## Important APIs, Types, And Functions
It sets `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Recursive Automake targets enter `delay-gen/src`, where the actual module library and headers are declared.

## State And Persistence Behavior
No runtime or persistent state is managed.

## Dependencies And Integration Points
It is reached from `xlators/debug/Makefile.am` and points the build system at `delay-gen/src/Makefile.am`.

## Risks
The only meaningful risk is accidentally omitting `src`, which would stop building delay-gen.

## Test Signals
Recursive build and install tests should show `delay-gen.la` produced from the `src` directory.
