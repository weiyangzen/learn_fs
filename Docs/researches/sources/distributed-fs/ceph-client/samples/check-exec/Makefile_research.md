<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/Makefile -->
# sources/distributed-fs/ceph-client/samples/check-exec/Makefile

## Purpose
The check-exec `Makefile` builds the userspace `inc` interpreter and `set-exec` securebits wrapper samples.

## Important APIs, Types, And Functions
It declares `userprogs-always-y := inc set-exec`, adds `-I usr/include`, and defines `all` and `clean` phony targets that recurse into the kernel sample build.

## Control Flow
Kbuild builds the listed userspace programs. The local `all` target invokes `$(MAKE) -C ../.. samples/check-exec/`; `clean` invokes kernel clean for `M=samples/check-exec/`.

## State And Persistence
There is no runtime state. Build outputs are the `inc` and `set-exec` sample binaries.

## Dependencies And Integration Points
It integrates with kernel samples Kbuild and generated UAPI include headers.

## Risks And Edge Cases
The BSD-3-Clause sample differs from most GPL samples but only affects source licensing. Incorrect relative invocation can fail if not run from the expected samples directory.

## Test Signals
`make samples/check-exec/` should build both binaries and `make -C ../.. M=samples/check-exec/ clean` should remove generated objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/Makefile -->
