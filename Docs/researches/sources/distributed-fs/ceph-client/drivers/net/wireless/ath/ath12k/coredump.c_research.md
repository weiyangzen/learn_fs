# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.c

## Purpose
Provides the enabled coredump implementation for firmware crash capture. It maps QMI memory-region types to ath12k dump TLV types, asks the bus/HIF layer to download dump memory, and uploads the assembled dump through Linux devcoredump.

## Important APIs, Types, And Functions
`ath12k_coredump_get_dump_type()` translates `ath12k_qmi_target_mem` values into `ath12k_fw_crash_dump_type`. `ath12k_coredump_collect()` delegates to `ath12k_hif_coredump_download()`. `ath12k_coredump_upload()` is a workqueue handler that calls `dev_coredumpv()` with `ab->dump_data` and `ab->ath12k_coredump_len`.

## Control Flow
Recovery calls collect before pre-reconfiguration. HIF/bus code fills `ab->dump_data` and schedules `ab->dump_work`. The upload worker logs the upload, hands buffer ownership to devcoredump, and clears the pointer.

## State And Persistence
Uses `ath12k_base.dump_data` and `ath12k_base.ath12k_coredump_len`. After `dev_coredumpv()`, ownership leaves the driver. Dump type mapping treats BDF/CALDB regions as no-dump and unknown regions as max/invalid.

## Dependencies And Integration Points
Depends on Linux `devcoredump`, HIF coredump download support, QMI memory-region enums, and debug logging. Integrated from `core.c` reset work and initialized as `ab->dump_work` in allocation.

## Risks
Ownership transfer is strict: `dev_coredumpv()` owns the buffer after upload. Incorrect length or partially filled dump data would expose malformed devcoredumps. Unsupported region mappings can silently omit data needed for diagnosis.

## Test Signals
Simulate firmware assert and verify `/sys/class/devcoredump` receives an ath12k dump. Validate region TLVs on hardware with HOST DDR, M3, pageable, and MLO global memory. Ensure repeated crashes do not reuse freed `dump_data`.
