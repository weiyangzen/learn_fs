# sources/distributed-fs/openafs/src/auth/test/Makefile.in

## Purpose
Builds auth subsystem test utilities for cell configuration, token cache behavior, and NetInfo/NetRestrict parsing.

## Important APIs, Types, and Functions
Targets are `testcellconf`, `ktctest`, and `testnetrestrict`. It links against libtool auth, sys, rx, util, opr, and cmd libraries plus roken.

## Control Flow
`tests all` builds all three binaries. Each target links one `.lo` object with shared `LT_deps` and `LT_libs`. `clean` removes libtool outputs, objects, binaries, and core files. `install` and `dest` are intentionally empty.

## State and Persistence
No runtime state. Build outputs are local test binaries and libtool artifacts.

## Dependencies and Integration Points
Includes top-level config, pthread, and libtool make fragments. The tests exercise APIs implemented by the surrounding `src/auth` code and are typically run from the source/build tree.

## Risks and Test Signals
These are utility-style tests rather than an automated assertion suite; several require local AFS configuration or tokens. Build validation should ensure all three targets compile under configured pthread/libtool settings and clean removes generated outputs.
