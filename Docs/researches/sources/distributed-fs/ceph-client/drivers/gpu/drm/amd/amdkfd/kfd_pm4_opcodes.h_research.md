
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_opcodes.h

## Purpose
Defines PM4 IT opcode values and PM4 packet type constants used by KFD packet builders.

## Important APIs, types, and functions
- `enum it_opcode_type` includes general PM4 opcodes and KFD/MES-specific scheduler opcodes: `IT_SET_RESOURCES`, `IT_MAP_PROCESS`, `IT_MAP_QUEUES`, `IT_UNMAP_QUEUES`, `IT_QUERY_STATUS`, and `IT_RUN_LIST`.
- `PM4_TYPE_0`, `PM4_TYPE_2`, and `PM4_TYPE_3` constants identify packet formats.

## Control flow
No executable code. Packet builders pass opcode constants to `pm_build_pm4_header`.

## State and persistence behavior
No runtime state. Values are firmware ABI constants and must remain stable.

## Dependencies and integration points
Included by VI and v9 packet-manager implementations. The opcode constants are encoded into `PM4_MES_TYPE_3_HEADER`.

## Risks
Changing numeric values breaks command processor decoding. The enum mixes many graphics/compute PM4 commands with KFD scheduler commands, so accidental reuse or typo in packet builders can submit a valid but wrong opcode.

## Test signals
Packet-builder dword dumps should show expected opcodes for every PM4 packet. Build coverage should include both VI and v9 packet managers.
