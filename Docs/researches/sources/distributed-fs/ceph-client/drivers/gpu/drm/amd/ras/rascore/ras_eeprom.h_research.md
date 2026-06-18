# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.h

Purpose: this header defines the physical EEPROM table contract and the public API used by core and UMC for persistent bad-page storage.

Important types and macros: table versions are `RAS_TABLE_VER_V1`, `RAS_TABLE_VER_V2_1`, and `RAS_TABLE_VER_V3`. Threshold modes include `NONSTOP_OVER_THRESHOLD`, `WARN_NONSTOP_OVER_THRESHOLD`, and `DISABLE_RETIRE_PAGE`. NPS/address packing helpers store bad-page PFN bits and NPS mode inside `eeprom_umc_record.retired_row_pfn`. `struct ras_eeprom_table_header` is the serialized table header. `struct ras_eeprom_table_ras_info` stores RMA status, health percent, and threshold. `struct ras_eeprom_control` tracks table geometry, I2C callbacks, limits, counters, mutex, and bad-channel bitmap. `struct eeprom_umc_record` is the in-memory bad-page record with serialized fields plus runtime-only current-NPS fields.

Control flow and state: the header has no active behavior, but it defines the persistent schema that `ras_eeprom.c`, `ras_umc.c`, and firmware EEPROM compatibility paths rely on. `ras_eeprom_append()`, `ras_eeprom_read()`, reset, count, sync, storage status, and health functions form the exported backend.

Dependencies and integration: it includes `ras_sys.h` for system callback types and forward-declares `ras_core_context`. Risks are ABI/layout related: the comment notes serialized record size differs from `sizeof(struct eeprom_umc_record)`, so callers must not write the struct directly. Test signals should verify packing macros, threshold mode behavior, and that runtime-only fields are reconstructed before callers use RAM bad-page records.
