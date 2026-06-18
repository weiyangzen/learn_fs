# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-katmai.c

## Purpose
Old U-Boot compatibility wrapper for Katmai 440SP-style boards.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info, installs `katmai_fixups()`, initializes FDT, and starts serial console. `katmai_fixups()` uses a fixed 33.333 MHz sysclk, applies 440SPE-like clocks, derives memory size from 440SPE MQ registers, writes Ethernet MAC index 0, and fixes EBC ranges. `BSS_STACK(4096)` provides a local wrapper stack.

## State, Dependencies, Risks, And Tests
State includes copied `bd_t`, platform fixup callback, BSS stack, and FDT updates. Dependencies include 4xx DCR helpers, 440SPE memory/clock logic, and EBC node path `/plb/opb/ebc`. Risks include hard-coded clock accuracy, single-MAC assumption, MQ memory-hole simplification, and EBC path mismatch. Test with `cuImage.katmai`, memory sizing above/below 4GB boundaries, and FDT EBC/MAC/clock inspection.
