# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.c

## Purpose
`coredump.c` is the devcoredump handoff for ath11k firmware crash data. It classifies firmware memory regions into dump TLV types, triggers HIF-specific dump collection, and uploads the assembled dump buffer to the kernel devcoredump facility.

## Important APIs, Types, And Functions
`ath11k_coredump_get_dump_type()` maps firmware region types such as host DDR, M3, and pageable memory to `enum ath11k_fw_crash_dump_type`, while ignoring BDF/CALDB regions. `ath11k_coredump_collect()` delegates collection to `ath11k_hif_coredump_download()`. `ath11k_coredump_upload()` is the workqueue callback that calls `dev_coredumpv()` with `ab->dump_data` and `ab->ath11k_coredump_len`.

## Control Flow
Crash/reset flow in `core.c` calls `ath11k_coredump_collect()`, allowing the active HIF implementation to download and assemble crash data into `ab->dump_data`. `ath11k_core_alloc()` initializes `ab->dump_work` to `ath11k_coredump_upload()`. When scheduled, upload logs a message, passes ownership of the dump buffer to devcoredump, and clears `ab->dump_data`.

## State And Persistence
The file uses `ath11k_base::dump_data` and `ath11k_coredump_len` as transient ownership state. Persistence is delegated to devcoredump, whose retention and userspace retrieval are kernel-managed.

## Dependencies And Integration Points
It depends on `CONFIG_DEV_COREDUMP`, Linux `devcoredump.h`, HIF coredump download support, and the dump-format definitions in `coredump.h`. It is integrated into reset recovery through `core.c`.

## Risks And Test Signals
The primary risk is buffer ownership: after `dev_coredumpv()` the driver must not free or reuse the buffer. Dump type mapping must stay aligned with firmware region identifiers. Test signals include forced firmware crash, presence of devcoredump artifact, correct TLV type classification, no double-free on dump upload, and graceful no-op behavior when devcoredump is disabled.
