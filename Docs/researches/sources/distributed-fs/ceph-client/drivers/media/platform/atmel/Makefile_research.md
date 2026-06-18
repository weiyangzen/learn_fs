# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Makefile

## Purpose
This Makefile maps the Atmel ISI Kconfig option to its driver object.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_VIDEO_ATMEL_ISI) += atmel-isi.o`.

## Control Flow
Kbuild includes `atmel-isi.o` as built-in or module according to `CONFIG_VIDEO_ATMEL_ISI`.

## State and Persistence
There is no runtime state. Its persistent effect is build artifact composition.

## Dependencies and Integration Points
The rule must stay aligned with `drivers/media/platform/atmel/Kconfig` and the `atmel-isi.c` source filename.

## Risks and Edge Cases
A stale object name or symbol mismatch makes the Kconfig option build nothing or fail during compilation.

## Test Signals
Enable `CONFIG_VIDEO_ATMEL_ISI=m` and confirm the module builds with no orphaned Kconfig symbol.
