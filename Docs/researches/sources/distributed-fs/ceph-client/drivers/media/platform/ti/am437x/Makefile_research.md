# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Makefile

## Purpose
Builds the AM437x VPFE capture driver object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_VIDEO_AM437X_VPFE) += am437x-vpfe.o` maps the Kconfig symbol directly to the driver object.

## Control Flow
No runtime flow. Kbuild includes the driver only when the symbol is enabled.

## State And Persistence
No runtime state; only build artifact generation.

## Dependencies And Integration Points
Connects `VIDEO_AM437X_VPFE` to `am437x-vpfe.c` in the TI media build.

## Risks
There are no split helper objects, so all VPFE functionality must compile from the single C file.

## Test Signals
Kernel build output should contain `am437x-vpfe.o` or `am437x-vpfe.ko` when enabled.
