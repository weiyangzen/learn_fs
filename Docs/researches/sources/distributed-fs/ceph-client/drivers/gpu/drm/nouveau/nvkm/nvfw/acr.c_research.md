# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/acr.c

## Purpose
Provides debug dump helpers for ACR WPR, LSB, and ACR descriptor structures across multiple firmware generations.

## Important APIs, types, and functions
Functions include `wpr_header_dump()`, `wpr_header_v1_dump()`, `wpr_header_v2_dump()`, `lsb_header_dump()`, `lsb_header_v1_dump()`, `lsb_header_v2_dump()`, `flcn_acr_desc_dump()`, and `flcn_acr_desc_v1_dump()`.

## Control flow, state, and persistence
All functions are read-only formatters: they accept parsed structure pointers and log fields with `nvkm_debug()`. They do not validate ranges or mutate state.

## Dependencies and integration points
Depends on `nvfw/acr.h` structure definitions and `core/subdev` logging. Used by ACR WPR parse/build/patch and HS firmware setup code.

## Risks and test signals
Debug output can reveal bad offsets, WPR ranges, signatures, and region masks. Since the functions do not enforce correctness, validation comes from downstream boot and WPR comparison failures.
