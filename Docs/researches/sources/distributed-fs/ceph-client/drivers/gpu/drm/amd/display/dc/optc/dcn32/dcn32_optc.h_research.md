# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn32/dcn32_optc.h

## Purpose
Defines DCN 3.2 OPTC field metadata and declares DCN32-specific helper functions. It is intentionally mask/shift focused because DCN32 reuses the DCN31 register list shape while adding fields needed for current master state, OPTC double-buffer pending, manual timing division, and pipe update status.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN3_2(mask_sh)` expands field mappings for timing, update lock, CRC, GSL, ODM data source, memory, DSC, DRR, pipe update, and interrupt-destination fields. Notable DCN32 fields include `OTG_CURRENT_MASTER_EN_STATE`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_H_TIMING_DIV_MODE_MANUAL`, and the pipe pending bits. Prototypes expose `dcn32_timing_generator_init()`, ODM bypass/segment helpers, horizontal timing manual mode, and ODM double-buffer wait.

## Control Flow and State
The header has no executable flow. It controls which hardware fields are available to the DCN32 vtable and inherited helper paths. The pending and manual-mode fields support synchronization decisions during ODM and timing changes.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`; later DCN35, DCN401, and DCN42 files include this header to reuse exported helpers and the field-list baseline. Register tables generated from this macro are consumed by `struct optc` initialization.

## Risks and Test Signals
Bad field mapping can break lock status, double-buffer polling, ODM setup, or CRC reads. Compile tests check symbol availability; functional tests should exercise update locks, ODM reconfiguration, DRR, and pipe update pending telemetry on DCN32 hardware.
