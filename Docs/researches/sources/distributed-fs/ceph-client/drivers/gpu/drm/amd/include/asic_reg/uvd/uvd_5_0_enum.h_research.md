# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_5_0_enum.h

## Purpose

`uvd_5_0_enum.h` provides typed integer enumerations for UVD 5.0 and adjacent AMDGPU hardware programming values. Unlike the offset and mask headers, this file exports C `typedef enum` types that give semantic names to command IDs, tiling modes, debug block IDs, formats, cache policies, performance counter modes, and memory power controls.

## Important APIs, Types, And Macros

Important enums include `UVDFirmwareCommand` for firmware command packet IDs such as fence, trap, decoded/bitstream/display addresses, pitch, tiling, and end-of-decode; endian and array/tiling geometry enums such as `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, group/row/bank/sample split, address-config pipe/interleave/shader-engine/GPU/lower-pipe enums; extensive debug block ID maps, including current, old, and BY2 naming schemes; color, surface, buffer, image data, and numeric format enums; tile type, micro/macro tiling, pipe/bank geometry enums; `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`; surface array/color/depth enums; SIMD count; and memory power force/disable/select enums.

## Control Flow And Data Flow

The file has no local control flow. Its values are consumed by command construction, register field encoding, debug/performance selection, memory tiling setup, format descriptors, and power-management programming. Values flow into packets or bitfields defined in companion register headers and firmware interfaces.

## State And Persistence Behavior

The enum constants are compile-time state only. When used in register writes or firmware packets, they select persistent hardware or firmware behavior such as surface interpretation, memory layout, cache policy, performance counter mode, debug block selection, and memory power mode.

## Dependencies And Integration Points

The file stands alone syntactically but is intended to be included by UVD 5.0 ASIC code and generated register consumers. It integrates with UVD firmware command submission, buffer/image metadata programming, tiling/address-library logic, debug/perf tooling, and power-management code.

## Risks And Test Signals

Risks include ABI drift in enum numeric values, duplicate/reserved names being treated as valid runtime choices, cross-generation reuse of debug block IDs, and mismatch between format enums and userspace/firmware expectations. Test signals include compile coverage, firmware command tests for each used `UVDFirmwareCommand`, decode/render format validation, tiling/address tests, perf/debug block selection smoke tests, and generated enum diffs. The duplicate `IMG_DATA_FORMAT_RESERVED_29` name/value in the source should be preserved as generated data unless the upstream register database changes.
