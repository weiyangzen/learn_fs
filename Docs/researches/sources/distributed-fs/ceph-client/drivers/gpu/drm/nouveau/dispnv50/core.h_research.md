<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h

## Purpose
This header defines the NV50 display core channel object, its generation-specific function table, and constructor/helper declarations for all supported core channel classes.

## Important APIs, Types, and Functions
`struct nv50_core` stores the function table, display pointer, DMA channel, and `assign_windows` flag. `struct nv50_core_func` declares hooks for init, notifier init/wait, caps init, update, window ownership, head/output function tables, and optional CRC support. The header declares core constructors, shared NV507D helpers, capability initializers, update functions, window owner helper, and output function tables for DAC/PIOR/SOR variants.

## Control Flow
There is no standalone flow. Runtime code selects a `nv50_core_func` and then calls its hooks during display init, atomic commits, capability setup, notifier synchronization, and output control.

## State and Persistence Behavior
The header describes persistent per-display core state. `assign_windows` marks whether modern core init should assign window ownership. Function tables encode generation behavior and indirectly control hardware state persistence through channel methods.

## Dependencies and Integration Points
It includes `disp.h`, `atom.h`, `crc.h`, and `nouveau_encoder.h`, and ties together head, output, CRC, and core channel implementation files.

## Risks
Function table fields are generation-specific; missing hooks cause runtime NULL dereferences or skipped hardware programming. CRC pointers are conditional on debugfs and must match build configuration. Shared helper declarations must match class-specific method layouts.

## Test Signals
Build with debugfs on/off, core init and update on all class families, notifier wait paths, caps initialization, window ownership on GV100+, and output control through DAC/SOR/PIOR validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h -->
