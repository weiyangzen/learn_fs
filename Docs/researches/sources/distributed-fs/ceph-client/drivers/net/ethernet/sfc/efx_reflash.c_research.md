# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_reflash.c

Purpose: Implements devlink flash-update backend for SFC/AMD adapters, including firmware image format detection, CRC validation, NVRAM partition selection, erase/write chunking, update finish/abort, and user progress reporting.

Important APIs and functions: Public `efx_reflash_flash_firmware()` performs the update. Static parsers recognize Reflash headers, SmartNIC image headers, and SmartNIC bundle headers. Helper `efx_reflash_partition_type()` maps firmware type/subtype to NVRAM partition type/subtype. Erase/write helpers split NVRAM operations into aligned chunks and report devlink status.

Control flow: The flash path checks firmware capability `BUNDLE_UPDATE`, serializes on `efx->reflash_mutex`, reports "Checking update", either selects AUTO partition or scans the firmware byte-by-byte for the first valid supported image header, verifies NVRAM subtype compatibility, queries partition info, rejects protected/unwritable/bad-size images, starts an NVRAM update, erases as needed, writes aligned chunks with padding for the final partial chunk, finishes with polled update completion, or aborts on failure. It reports final success/failure through devlink.

State and persistence: Mutates persistent NVRAM contents on the adapter. Runtime state is limited to the reflash mutex, temporary buffers, MCDI update transaction state, and devlink progress notifications.

Dependencies and integration points: Uses `fw_formats.h` header offsets/magic values, Linux firmware blobs, CRC32 helpers, devlink flash APIs, MCDI NVRAM metadata/info/erase/write/update commands, NIC type capabilities such as `flash_auto_partition` and `mcdi_max_ver`, and extack for user errors. Called from `efx_devlink.c`.

Risks: Firmware scanning is intentionally permissive and stops at the first candidate, even if unsupported. CRC and overflow checks protect parsing but final compatibility is delegated to running firmware. Erase/write alignment must match partition metadata. Failed writes must call update-finish abort without masking original errors. Updating NVRAM is destructive and persistent, so subtype/protection checks are critical.

Test signals: Valid and invalid Reflash/SmartNIC/bundle images, prepended signed-container data, CRC mismatch, unsupported firmware type, subtype mismatch, auto partition devices, protected/unwritable partitions, image too large, erase/write MCDI failures, final update timeout, concurrent update attempts, and devlink status progress.
