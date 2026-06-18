# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.h

## Purpose

`amdgpu_ras_eeprom.h` declares the persistent RAS EEPROM table format and API used by AMDGPU RAS code. It defines table versions, GPU health and EEPROM error enums, packed persistent structures, live table-control state, bad-page record layout, EEPROM lifecycle functions, SMU-managed EEPROM wrappers, and debugfs file operations.

## Important APIs, Types, And Constants

- Versions: `RAS_TABLE_VER_V1`, `RAS_TABLE_VER_V2_1`, and `RAS_TABLE_VER_V3`.
- Health states: `enum amdgpu_ras_gpu_health_status` distinguishes usable GPUs from GPUs retired because ECC reached threshold.
- Record error states: `enum amdgpu_ras_eeprom_err_type` defines ignore/not-applicable, recoverable, non-recoverable, and count sentinel.
- `struct amdgpu_ras_eeprom_table_header` stores signature, version, first record offset, table size, and checksum.
- `struct amdgpu_ras_eeprom_table_ras_info` stores V2.1+ RMA status, health percent, ECC page threshold, and reserved padding.
- `struct amdgpu_ras_eeprom_control` stores decoded header/RAS info, EEPROM base address, offsets, current/old record counts, bad-page count, MCA/PA record counts, first record index, max capacity, mutex, bad-channel bitmap, and validity flag.
- `struct eeprom_table_record` stores bad-page record data: MCA address or offset, retired page, timestamp, error type, bank/CU, memory channel, and MCUMC ID.
- Lifecycle/check APIs: `amdgpu_ras_eeprom_init()`, `amdgpu_ras_eeprom_reset_table()`, `amdgpu_ras_eeprom_check()`, and `amdgpu_ras_eeprom_check_and_recover()`.
- Read/write APIs: `amdgpu_ras_eeprom_read()`, `amdgpu_ras_eeprom_read_idx()`, `amdgpu_ras_eeprom_append()`, `amdgpu_ras_eeprom_update_record_num()`, and `amdgpu_ras_eeprom_max_record_count()`.
- Threshold/status APIs: `amdgpu_ras_eeprom_check_err_threshold()` and `amdgpu_ras_check_bad_page_status()`.
- SMU wrappers: support check, table-version getter, bad-page count getter, bad-page MCA/IPID/timestamp getters, timestamp setter, and erase function.
- Debugfs exports: `amdgpu_ras_debugfs_set_ret_size()`, `amdgpu_ras_debugfs_eeprom_size_ops`, and `amdgpu_ras_debugfs_eeprom_table_ops`.

## Control Flow

Callers initialize `amdgpu_ras_eeprom_control` through `amdgpu_ras_eeprom_init()`, then RAS recovery reads records with `amdgpu_ras_eeprom_read()` or `amdgpu_ras_eeprom_read_idx()`. New retired pages are appended with `amdgpu_ras_eeprom_append()`.

Validation is explicit. `amdgpu_ras_eeprom_check()` verifies integrity and threshold/RMA state after load. `amdgpu_ras_eeprom_check_and_recover()` can reset and rewrite the persistent table from live bad-page state if checksum verification fails.

SMU-managed EEPROM uses the same high-level API but branches through `amdgpu_ras_smu_eeprom_supported()` and the SMU wrappers for version, count, MCA address, IPID, timestamp, and erase operations.

Debugfs setup in `amdgpu_ras.c` uses the exported file operations and updates formatted file size through `amdgpu_ras_debugfs_set_ret_size()` after table size changes.

## State And Persistence Behavior

`tbl_hdr` and `tbl_rai` mirror persistent EEPROM data. Offsets, counts, `ras_fri`, `ras_max_record_count`, `bad_channel_bitmap`, mutex, and `is_eeprom_valid` are driver bookkeeping.

`ras_num_recs` is active record count. `ras_num_recs_old` supports SMU count polling. `ras_num_bad_pages` can differ from record count because records can represent retire units or multiple pages depending on ASIC generation.

`ras_num_mca_recs` and `ras_num_pa_recs` track mixed old/new record formats. `ras_fri` is the first readable circular-buffer index, so logical record order may not equal physical EEPROM offset order.

`is_eeprom_valid` prevents higher-level code from saving into known corrupt or unrecoverable EEPROM state.

## Dependencies And Integration Points

The header includes `<linux/i2c.h>`, forward-declares `struct amdgpu_device`, is embedded through `amdgpu_ras.h`, and exports debugfs file operations for `amdgpu_ras.c`. Its API is used by RAS recovery, UMC bad-page conversion, SMU/PMFW EEPROM support, DPM/CPER threshold notification, and debugfs table presentation.

## Risks And Edge Cases

- `eeprom_table_record` is packed but not the same size as the 24-byte persistent record because it contains `uint64_t` and enum fields.
- The `address/offset` and `bank/cu` unions are context-dependent across PA records, MCA records, and SMU-managed records.
- `ras_num_bad_pages` and `ras_num_recs` are not equivalent.
- `ras_fri` and version-specific record offsets must both be respected for circular reads.
- Adding a table version requires coordinated changes in reset, init, read, check, and bad-page conversion code.
- `is_eeprom_valid` is advisory; incorrect updates can either block valid saves or permit writes to corrupt state.

## Test Signals

- Verify packed field offsets and serialization assumptions.
- Test record count, bad-page count, MCA count, PA count, and retire-unit expansion separately.
- Validate local-I2C and SMU-managed implementations through the same high-level read/append/reset/check scenarios.
- Confirm debugfs size and unsupported output after reset, append, and context absence.
- For new table versions, test old-version load, migration, reset, checksum, threshold, and recovery paths.
