# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Makefile

## Purpose
This Makefile maps Cadence CSI-2 RX and TX Kconfig symbols to driver objects.

## Important APIs, Types, and Functions
The object rules are `obj-$(CONFIG_VIDEO_CADENCE_CSI2RX) += cdns-csi2rx.o` and `obj-$(CONFIG_VIDEO_CADENCE_CSI2TX) += cdns-csi2tx.o`.

## Control Flow
Kbuild evaluates each tristate and includes the corresponding bridge driver object as built-in or module.

## State and Persistence
There is no runtime state. It only controls build composition.

## Dependencies and Integration Points
The rules must match the Kconfig symbols and C source filenames in the Cadence platform directory.

## Risks and Edge Cases
Filename or symbol mismatches break selected builds or leave enabled drivers without objects.

## Test Signals
Enable each Cadence symbol as `m` and confirm the expected modules are produced.
