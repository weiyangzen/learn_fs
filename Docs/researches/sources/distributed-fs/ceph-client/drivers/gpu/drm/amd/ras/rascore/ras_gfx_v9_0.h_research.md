# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.h

Purpose: this header defines the driver-visible GFX v9 RAS subblock enumeration and exposes the v9 function table.

Important definitions: `enum ras_gfx_v9_subblock` enumerates CPC, CPF, CPG, GDS, SPI, SQ, SQC ranges, TA, TCA, TCC ranges, TCI, TCP, TD, EA ranges, and UTC/ATC units. Range start/end constants are embedded in the enum to support validation and grouping. `extern const struct ras_gfx_ip_func gfx_ras_func_v9_0` is implemented by `ras_gfx_v9_0.c`.

Control flow and state: no code or persistence exists here. The enum values are an ABI-like contract with the v9 mapping table and callers that request injection subblocks.

Dependencies and integration: included by generic GFX dispatch and the v9 implementation. PSP error injection ultimately depends on these values being stable and aligned with the TA enum table. Risks include accidental renumbering, missing table entries for enum values, and confusing similarly named driver and TA enums. Test signals should include compile-time or unit checks that the table length covers `RAS_GFX_V9__GFX_MAX`, that expected range endpoints match table groups, and that user-facing injection requests map to supported TA subblocks.
