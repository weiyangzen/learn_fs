# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.h

## Purpose
Declares the etnaviv PPU flop-reset workaround interface.

## Important APIs, Types, and Functions
Forward-declares `struct etnaviv_chip_identity`, `struct etnaviv_drm_private`, and `struct etnaviv_gpu`; declares `etnaviv_flop_reset_ppu_require`, `etnaviv_flop_reset_ppu_init`, and `etnaviv_flop_reset_ppu_run`.

## Control Flow
No executable flow. GPU initialization uses `require`/`init`; ring initialization uses `run`.

## State and Persistence
The header exposes no state directly; implementation stores payload state in `etnaviv_drm_private`.

## Dependencies and Integration Points
Included by buffer/GPU paths and the implementation. It isolates the workaround from generic command buffer code.

## Risks
Callers must initialize the payload before running the workaround and only run when identity checks require or force it.

## Test Signals
Build coverage and affected-chip initialization paths validate this interface.
