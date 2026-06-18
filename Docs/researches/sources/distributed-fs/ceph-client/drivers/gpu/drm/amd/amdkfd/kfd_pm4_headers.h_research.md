
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers.h

## Purpose
Defines a small legacy PM4 type-3 header and map-process packet layouts used by older KFD packet code, plus the cache-flush event constant shared by release-mem packets.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER` exposes opcode, count, and type fields.
- `struct pm4_map_process` and `struct pm4_map_process_scratch_kv` describe map-process packet payloads for legacy hardware variants.
- `CACHE_FLUSH_AND_INV_TS_EVENT` names the release-mem event type.

## Control flow
This header contains no executable control flow. Included C files cast dword buffers to these structures and write bitfields before submitting them to firmware.

## State and persistence behavior
No runtime state. The structs are binary packet contracts; their layout effectively persists as an ABI with command processor/MES firmware.

## Dependencies and integration points
Uses standard fixed-width integer types from including files. Protected with `PM4_MES_HEADER_DEFINED` and per-structure include guards so it can coexist with generation-specific PM4 headers.

## Risks
Compiler bitfield layout, field widths, and spelling differences (`u32all` versus `u32All` in other headers) are fragile. Layout changes break firmware command decoding. Legacy structs overlap conceptually with VI/AI headers, so accidental mixed inclusion can select the wrong packet shape.

## Test signals
Build all KFD packet-manager variants with this header included transitively; validate `sizeof` and emitted dwords for legacy MAP_PROCESS packets if the legacy path is enabled.
