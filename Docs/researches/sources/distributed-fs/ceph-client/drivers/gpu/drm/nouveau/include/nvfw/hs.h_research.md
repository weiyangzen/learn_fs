
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/hs.h

## Purpose
Defines high-secure firmware headers and load headers for Nouveau's secure falcon firmware parsing.

## Important APIs, types, and functions
- `struct nvfw_hs_header` and `nvfw_hs_header()` describe the base HS header: signature, patch locations, metadata, header offset, and app version.
- `struct nvfw_hs_header_v2` and parser add patch signature, num_sig, fuse version, engine id, ucode id, and dependency map.
- `struct nvfw_hs_load_header` and `nvfw_hs_load_header_v2` describe non-secure/secure code offsets and sizes, data DMA base, code entry point, and app code/data offsets.

## Control flow
No executable logic is included. Parser implementations choose the correct versioned struct and return typed pointers into firmware data.

## State and persistence
No state is stored. These structs represent firmware metadata used during secure code loading and verification.

## Dependencies and integration points
Forward declares `struct nvkm_subdev`. It integrates with falcon boot, ACR, and secure firmware loading code.

## Risks
Security-sensitive fields include signatures, fuse version, engine id, dependency map, and secure code offsets. Misparsing can either reject valid firmware or load unauthenticated/wrong code.

## Test signals
Known-good HS firmware should parse and boot. Truncated headers, bad offsets, and invalid signature metadata should be rejected with useful diagnostics.
