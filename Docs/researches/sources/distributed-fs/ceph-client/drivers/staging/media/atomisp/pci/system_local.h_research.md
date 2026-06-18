# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.h

## Purpose
Declares the local AtomISP base-address map exported by `system_local.c`.

## Important APIs, Types, and Functions
Declares `GP_FIFO_BASE`, all `extern const hrt_address` base arrays for ISP/SP/MMU/DMA/IRQ/GDC/input-system blocks, and the single `GP_TIMER_BASE`.

## Control Flow
No execution. Callers include this header to access register base arrays.

## State and Persistence Behavior
The declared objects are immutable address-map state supplied by the C file.

## Dependencies and Integration Points
Defines `HRT_USE_VIR_ADDRS` under `HRT_ISP_CSS_CUSTOM_HOST`, includes `system_global.h` and deprecated `hive_types.h`. Used by hardware device accessors and CSS global structures.

## Risks
All declarations must stay synchronized with `system_local.c`. Virtual-address configuration affects host builds and address interpretation.

## Test Signals
Compile/link coverage for all extern arrays and runtime hardware access through each declared base.
