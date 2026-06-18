# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.c

## Purpose

`amdgpu_ras_eeprom.c` implements persistent RAS bad-page table storage. It detects platform support, locates the EEPROM table in I2C address space or delegates to SMU-managed EEPROM, initializes/resets table metadata, serializes and deserializes records, appends records with circular-buffer semantics, verifies and repairs checksums, updates RMA/health status, exposes debugfs table dumps, and wraps SMU/PMFW RAS EEPROM operations.

## Important APIs, Types, And Functions

- Layout constants: `EEPROM_I2C_MADDR_0`, `EEPROM_I2C_MADDR_4`, `RAS_TABLE_HEADER_SIZE`, `RAS_TABLE_RECORD_SIZE`, `RAS_TABLE_HDR_VAL`, `RAS_TABLE_HDR_BAD`, `RAS_TBL_SIZE_BYTES`, `RAS_RECORD_START`, `RAS_RECORD_START_V2_1`, and max-record constants.
- Index macros: `RAS_INDEX_TO_OFFSET()`, `RAS_OFFSET_TO_INDEX()`, `RAS_RI_TO_AI()`, `RAS_NUM_RECS()`, and `RAS_NUM_RECS_V2_1()`.
- Platform setup: `__is_ras_eeprom_supported()` and `__get_eeprom_i2c_addr()` gate support and select EEPROM base address.
- Serialization: header, RAS-info, and record encode/decode helpers translate host structures to little-endian EEPROM bytes.
- Table mutation: `amdgpu_ras_eeprom_reset_table()`, `amdgpu_ras_eeprom_append()`, `amdgpu_ras_eeprom_append_table()`, `amdgpu_ras_eeprom_update_header()`, and `amdgpu_ras_eeprom_correct_header_tag()`.
- Table reads/checks: `amdgpu_ras_eeprom_init()`, `amdgpu_ras_eeprom_read()`, `amdgpu_ras_eeprom_read_idx()`, `amdgpu_ras_eeprom_check()`, `__verify_ras_table_checksum()`, and `amdgpu_ras_eeprom_check_and_recover()`.
- Threshold/RMA: `amdgpu_ras_eeprom_check_err_threshold()`, `amdgpu_ras_smu_eeprom_check()`, `amdgpu_ras_smu_eeprom_append()`, and `amdgpu_ras_check_bad_page_status()`.
- Debugfs: `amdgpu_ras_debugfs_eeprom_size_ops`, `amdgpu_ras_debugfs_eeprom_table_ops`, and `amdgpu_ras_debugfs_set_ret_size()`.
- SMU wrappers: `amdgpu_ras_smu_eeprom_supported()`, table version/count/address/timestamp/IPID getters, and `amdgpu_ras_smu_erase_ras_table()`.

## Control Flow

`amdgpu_ras_eeprom_init()` delegates to SMU init when PMFW owns RAS EEPROM. Otherwise it validates support and I2C adapter presence, resolves the EEPROM address, initializes the mutex, reads and decodes the 20-byte header, creates a new table on unknown signature, resets old tables on selected HBM3E variants, decodes version-specific record counts and offsets, validates capacity, and sets the first record index.

`amdgpu_ras_eeprom_reset_table()` writes a clean local EEPROM table or asks SMU to erase its table. Local reset chooses V1/V2.1/V3 from UMC IP version, initializes V2.1+ RAS info, computes checksum, writes header and optional RAS info, clears counts and channel bitmap, notifies DPM of zero bad pages/channels, clears saved-count state, and refreshes debugfs file size.

`amdgpu_ras_eeprom_append()` validates local appends, temporarily encodes NPS partition bits into `retired_page`, locks the table, serializes records, writes one or two circular ranges, advances `ras_fri` on overwrite, updates counts, recomputes checksum/header/RAS info, updates debugfs size, unlocks, and clears the temporary NPS bits. SMU-managed append updates local count/RMA state while PMFW owns persistence.

`amdgpu_ras_eeprom_read()` reads active records from the circular table, handling wrap from `ras_fri` to zero. SMU-managed reads obtain MCA address, IPID, and timestamp per index, parse IPID through UMC callbacks, and fill records with MCA metadata.

`amdgpu_ras_eeprom_check()` verifies checksum and threshold state. A normal `AMDR` table is checked and warned at 90 percent threshold. A `BADG` table may be corrected back to `AMDR` if threshold policy now allows more records; otherwise custom thresholds mark RMA. `amdgpu_ras_eeprom_check_and_recover()` resets and re-saves in-memory bad pages when checksum recovery is possible.

Debugfs table reads format a virtual text file from header and records, supporting partial reads through `*pos` and reading one EEPROM record at a time.

## State And Persistence Behavior

The local table is a circular log. `ras_fri` points at the first readable record, `ras_num_recs` is the active count, and appends can overwrite old records. V1 stores header plus records; V2.1/V3 insert a 256-byte RAS info area with RMA status, health percentage, and threshold.

Persistent records are 24 bytes. In-memory `eeprom_table_record` fields are larger and are serialized with 48-bit masks for address/offset and retired page.

The checksum is a byte sum over header without checksum, optional RAS info, and active record bytes, negated so the total verifies to zero.

`AMDR` means a normal table. `BADG` means threshold-exceeded/retired state for custom thresholds. `ras->is_rma` mirrors this policy into runtime recovery behavior.

SMU-managed EEPROM stores authoritative records in PMFW; the driver retrieves version, count, MCA address, IPID, timestamp, and erase status through function pointers.

## Dependencies And Integration Points

The file depends on `amdgpu_eeprom_read/write()` over `adev->pm.ras_eeprom_i2c_bus`, ATOM/VBIOS address discovery, reset-domain semaphores for most I2C operations, `amdgpu_ras.c` context and bad-page counts, DPM/SMU notifications, UMC IPID parsing, CPER generation, debugfs file ops, UniRAS safety-watermark checks, and `ras_smu_drv` callbacks.

## Risks And Edge Cases

- Address selection depends on MP1 IP version, VBIOS part-number matching, and atom firmware data.
- Circular-buffer wrap arithmetic controls data retention and can silently overwrite oldest records.
- `__verify_ras_table_checksum()` does not take the reset-domain semaphore around its EEPROM read, unlike many other accessors.
- `record_err_type_str[record.err_type]` in debugfs has no visible bounds check for corrupted record data.
- SMU-managed append only updates local count/RMA state; actual persistence correctness depends on PMFW.
- `amdgpu_ras_eeprom_correct_header_tag()` updates checksum by delta and assumes current in-memory header/checksum are consistent.
- Unsupported platforms often return success (`0`), so callers need separate support checks if persistence is mandatory.

## Test Signals

- Initialize all supported MP1/UMC combinations, APU/non-APU variants, HBM3E reset quirk, and VBIOS address cases.
- Create and validate V1, V2.1, and V3 tables, offsets, capacities, RAS info, and checksums.
- Append records that fit, wrap, and overwrite; read back order, `ras_fri`, counts, PA/MCA counters, and debugfs output.
- Corrupt signatures, versions, checksums, record counts, and RAS info; verify reset, rejection, repair, and recovery.
- Test threshold modes `0`, `-1`, `-2`, and custom positive values, including CPER and RMA notifications.
- Exercise SMU function-pointer missing paths, count-update retry behavior, and IPID parsing.
- Test partial debugfs reads and EEPROM access during reset/recovery.
