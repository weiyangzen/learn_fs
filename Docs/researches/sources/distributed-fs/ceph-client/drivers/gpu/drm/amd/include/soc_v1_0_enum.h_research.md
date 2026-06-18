# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_enum.h

## Purpose

This header is a very small SOC v1.0 register-value vocabulary header. It defines symbolic values for memory type selection and shader memory alignment mode fields used by AMD GPU register programming code. It has no executable code; its value is in preserving exact numeric encodings expected by SOC v1.0 hardware and by any generated register programming paths that consume these enums.

## Important APIs, Types, and Constants

- `typedef enum MTYPE`: memory type encodings:
  - `MTYPE_NC = 0x0`
  - `MTYPE_RESERVED_1 = 0x1`
  - `MTYPE_RW = 0x2`
  - `MTYPE_UC = 0x3`
- `typedef enum SH_MEM_ALIGNMENT_MODE`: shader memory alignment encodings:
  - `SH_MEM_ALIGNMENT_MODE_DWORD = 0x0`
  - `SH_MEM_ALIGNMENT_MODE_UNALIGNED = 0x1`
- The include guard is `__SOC_V1_0_ENUM_H__`.

## Control Flow

There is no runtime control flow. Including this file only introduces enum tags and typedef names into the translation unit. Consumers choose enum constants while building register values or hardware-facing command/configuration structures.

## State and Persistence Behavior

The header owns no mutable state and performs no persistence. The constants may become persistent indirectly when written into GPU registers, firmware-visible buffers, saved queue descriptors, or command streams by downstream driver code. Any ABI or hardware compatibility comes from the stable numeric enum values, not from state in this file.

## Dependencies and Integration Points

The file has no explicit includes. It relies on C enum semantics and can be included by low-level AMDGPU register programming code. Integration points are likely SOC v1.0 hardware init/configuration code, shader memory configuration code, and any packet or register builders that need human-readable names for memory/cache behavior.

## Risks

- The numeric values are hardware ABI. Renumbering or reusing the reserved slot can silently program incorrect memory/cache behavior.
- The enum names are generic (`MTYPE`, `SH_MEM_ALIGNMENT_MODE`) and may collide if included with other generated register headers that use the same global names.
- There are no compile-time assertions connecting these values to register field widths; consumers must mask/shift them correctly.
- `MTYPE_RESERVED_1` should remain reserved unless hardware documentation and all consumers are updated.

## Test Signals

- Compile coverage from AMDGPU translation units that include this header is the main signal.
- Register programming tests or hardware bring-up logs should confirm expected cache/memory type behavior for SOC v1.0 paths.
- Static checks can compare the enum values against generated register documentation or golden headers.
- Runtime failures would likely appear as GPU faults, incorrect memory coherency, or shader memory access anomalies rather than local failures in this header.
