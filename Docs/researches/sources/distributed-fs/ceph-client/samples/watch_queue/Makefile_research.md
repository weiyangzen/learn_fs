# sources/distributed-fs/ceph-client/samples/watch_queue/Makefile

## Purpose
This kbuild fragment declares the `watch_test` userspace sample for the watch queue API.

## APIs, Types, And Functions
It uses `userprogs-always-y += watch_test` and adds `usr/include` to `userccflags` so generated UAPI headers are visible.

## Control Flow
During sample builds, kbuild compiles `watch_test.c` as a userspace program whenever this sample directory is included.

## State And Persistence
No runtime state is held by the Makefile. It only contributes build variables.

## Dependencies And Integration Points
It integrates with kernel samples kbuild and depends on generated watch queue/keyctl UAPI headers.

## Risks And Test Signals
Risks are limited to header include path drift or omitted generated headers. Test signal is a successful `watch_test` binary build.
