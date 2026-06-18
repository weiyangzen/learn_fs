# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Makefile

## Purpose
Defines the build recipe for the DIM2 MOST module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MOST_DIM2)` builds `most_dim2.o`, composed from `dim2.o` and `hal.o`.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Ties the platform/MOST interface layer to the DIM2 HAL implementation.

## Risks And Test Signals
Both objects are required; omitting `hal.o` would leave DIM API symbols unresolved. Test signal is a targeted `M=drivers/staging/most/dim2` build.
