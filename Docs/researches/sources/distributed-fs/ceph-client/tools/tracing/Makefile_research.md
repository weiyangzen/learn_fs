# sources/distributed-fs/ceph-client/tools/tracing/Makefile

## Purpose
This top-level tracing tools Makefile dispatches build, install, and clean targets to the `latency` and `rtla` subdirectories.

## Important APIs, Types, and Functions
It includes `../scripts/Makefile.include` and uses its `$(call descend,dir[,target])` helper. Public targets are `all`, `clean`, `install`, `latency`, `latency_install`, `latency_clean`, `rtla`, `rtla_install`, and `rtla_clean`.

## Control Flow
`all` depends on both `latency` and `rtla`. `install` depends on both install subtargets. `clean` depends on both clean subtargets. Each subtarget descends into the corresponding child directory and optionally passes `install` or `clean`.

## State and Persistence
The file itself does not persist state, but its targets delegate object, binary, installation, and cleanup behavior to child Makefiles. Install writes are controlled by those children and `DESTDIR`.

## Dependencies and Integration Points
The Makefile integrates with the Linux kernel tools build infrastructure through `Makefile.include`. It assumes the `latency/` and `rtla/` directories provide compatible Makefiles.

## Risks and Edge Cases
Any missing or incompatible child Makefile causes top-level tracing builds to fail. Because this wrapper has no feature probing of its own, child failures are surfaced only after descent.

## Test Signals
Run `make`, `make latency`, `make rtla`, `make clean`, and `make install DESTDIR=...` from `tools/tracing` and confirm the expected child targets are invoked.
