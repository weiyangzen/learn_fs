# sources/distributed-fs/ceph-client/samples/watchdog/Makefile

## Purpose
This kbuild fragment declares the `watchdog-simple` userspace watchdog sample.

## APIs, Types, And Functions
It uses `userprogs-always-y += watchdog-simple` to request unconditional sample build.

## Control Flow
There is no runtime flow. Kbuild consumes this variable to compile `watchdog-simple.c`.

## State And Persistence
No state is held here beyond build metadata.

## Dependencies And Integration Points
It integrates with the kernel samples userspace-program build path and the watchdog sample source.

## Risks And Test Signals
The only meaningful risk is the source not compiling under sample kbuild. The test signal is the presence of the built `watchdog-simple` binary.
