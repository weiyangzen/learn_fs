# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/enum.c

## Purpose
This file provides small formatting helpers for NVKM enum and bitfield tables.

## Important APIs, Types, and Functions
Public functions are `nvkm_enum_find` and `nvkm_snprintbf`.

## Control Flow
`nvkm_enum_find` linearly scans a sentinel-terminated enum table for a matching value. `nvkm_snprintbf` scans a bitfield table and appends names for set bits into a caller buffer separated by spaces, then null-terminates.

## State and Persistence Behavior
No persistent state exists.

## Dependencies and Integration Points
It depends on NVKM enum/bitfield table definitions and is used by logging/debug paths.

## Risks
`nvkm_snprintbf` only prints known set bits and ignores unknown bits. Buffer size handling relies on `scnprintf`; output truncation is possible but null-terminated.

## Test Signals
Signals include table lookup hits/misses, bitfield formatting with multiple bits, empty values, and small buffer truncation.
