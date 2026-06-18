# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Makefile

## Purpose
`82xx/Makefile` maps PQ2/82xx config symbols to object files.

## Important APIs, Types, and Functions
`pq2.o` is built with `CONFIG_CPM2`, `ep8248e.o` with `CONFIG_EP8248E`, and `km82xx.o` with `CONFIG_MGCOGE`.

## Control Flow, State, and Persistence
This is build-time state only. The common restart implementation is tied to CPM2 availability, while each board object contributes its own machine definition.

## Dependencies and Integration Points
It integrates Kconfig board symbols with the PowerPC platform build and the shared CPM2/PQ2 support.

## Risks and Test Signals
Risks are minimal but include omitting common PQ2 code for a board that needs `pq2_restart()`. Test signals are successful targeted board builds and link resolution for machine hooks.
