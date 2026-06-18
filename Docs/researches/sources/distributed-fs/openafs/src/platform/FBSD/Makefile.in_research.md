# sources/distributed-fs/openafs/src/platform/FBSD/Makefile.in

## Purpose
Provides the FreeBSD platform makefile placeholder for an otherwise empty platform-specific support directory.

## Important APIs, Types, And Functions
Defines no-op `all`, `install`, `dest`, and `clean` targets, plus `SHELL=/bin/sh`.

## Control Flow
Platform dispatch can `cd` into `FBSD` and run any standard target without building or staging files.

## State And Persistence
No artifacts or persistent state are produced.

## Dependencies And Integration Points
Integrated by `src/platform/Makefile.in` through `$(MKAFS_OSTYPE)`. It protects FreeBSD builds from missing-target failures while leaving actual FreeBSD support elsewhere in the tree.

## Risks And Test Signals
Risk is that future FreeBSD-specific files added to this directory would need real target wiring. Test signal is successful no-op execution under FreeBSD build configurations.
