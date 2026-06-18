# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c

## Purpose

`fbnic_devlink.c` implements the driver's devlink surface: device allocation/registration, devlink info reporting, PLDM firmware flashing, firmware and OTP health reporters, firmware coredump collection, and helper reporting into both devlink health and the firmware log cache. It bridges Linux devlink/PLDM firmware infrastructure to FBNIC firmware mailbox TLVs and selected BAR4 OTP registers.

## Important APIs, Types, And Functions

`fbnic_devlink_alloc()`, `fbnic_devlink_free()`, `fbnic_devlink_register()`, and `fbnic_devlink_unregister()` wrap devlink allocation and lifecycle. Allocation stores the `struct fbnic_dev` in devlink private memory, sets PCI driver data, captures BAR mappings (`uc_addr0`, `uc_addr4`), DSN, PCIe MPS/read request/relaxed ordering values, and initializes `mac_addr_boundary`.

`fbnic_devlink_info_get()` publishes running and stored firmware, bootloader, UNDI versions, commit strings, and DSN serial number. Helper functions `fbnic_version_running_put()` and `fbnic_version_stored_put()` format version codes with `fbnic_mk_fw_ver_str()` and optionally add `.commit` entries.

Firmware flash uses PLDM callbacks `fbnic_pldm_match_record()` and `fbnic_flash_component()` via `fbnic_pldmfw_ops`, exposed through `fbnic_devlink_flash_update()`. Flashing maps QSPI component IDs to names, starts upgrade with `fbnic_fw_xmit_fw_start_upgrade()`, waits for firmware chunk requests, sends chunks with `fbnic_fw_xmit_fw_write_chunk()`, validates offset/length sequencing, and reports progress through devlink status notifications.

Health reporting uses `fbnic_fw_ops` and `fbnic_otp_ops`. `fbnic_fw_reporter_dump()` forces/reads firmware coredumps in TLV-sized chunks and emits a binary fmsg. `fbnic_fw_reporter_diagnose()` reports last heartbeat firmware uptime. `fbnic_devlink_fw_report()` and `fbnic_devlink_otp_check()` raise health reports and mirror messages into firmware logs when available.

## Control Flow

Info get is linear: add running mgmt, running bootloader, stored mgmt, stored bootloader, stored UNDI, then optional DSN serial. Each devlink call can abort on error.

PLDM flashing first validates PCI identity through `pldmfw_op_pci_match_record()`, then scans vendor-defined descriptors for `AntiRollbackVer`. Images older than `fbd->fw_cap.anti_rollback_version` are rejected with a devlink status update. For each supported component, a completion for `FW_WRITE_CHUNK_REQ` is registered before `FW_START_UPGRADE_REQ` so the driver can catch both firmware ACK and first chunk request. The loop waits for a completion, validates `offset == previous offset + previous length`, rejects oversized or out-of-range requests, sends data chunks, and terminates when firmware sends a finish request that collapses length to zero. On error it sends a cancel/error chunk response.

Firmware coredump dump first asks for size, handles firmware errors or zero size, allocates one completion large enough for a pointer table plus dump bytes, issues chunk reads sequentially, waits and reinitializes completion after each chunk, verifies each expected chunk pointer was consumed by the parser, then emits the full binary through devlink fmsg.

## State And Persistence

The devlink object owns `struct fbnic_dev` memory. Runtime device state includes firmware capability data, DSN, PCIe attributes, health reporter pointers, and BAR mappings. Flashing does not persist in host files; it writes device firmware storage through firmware mailbox protocol. Health reporter state persists while reporters are registered. Firmware logs are mirrored into the in-memory log ring when `fbnic_fw_log_ready()` is true.

## Dependencies And Integration Points

Dependencies include Linux devlink, PLDM firmware flashing, PCI helpers, unaligned endian helpers, FBNIC firmware mailbox functions, TLV maximum sizes, OTP CSR definitions, and firmware log support. It integrates with probe/remove lifecycle, `fbnic_fw.c` mailbox completions, `fbnic_fw_log.c` log storage, and ethtool/devlink userspace tooling.

## Risks And Edge Cases

Firmware flashing is sequencing-sensitive. Completion setup must precede the start request or the first firmware chunk request can be missed. Offset/length validation prevents malformed firmware requests from reading outside the image; changes must preserve those guards. Anti-rollback parsing assumes a vendor-defined descriptor shape of at least 21 bytes with a specific marker. Coredump allocation size is `sizeof(void *) * index_count + size`; large dumps can fail allocation. The coredump loop treats a still-non-NULL data pointer as missing data because the parser nulls entries after copying. Health reporter destroy must run for both reporters if OTP creation fails after FW reporter creation.

## Test Signals

Useful signals include `devlink dev info` showing all expected running/stored versions and serial, PLDM flash success/failure across each component ID, rejection of old anti-rollback images, timeout and malformed chunk negative paths, firmware coredump dump with multi-chunk payloads, health reports on heartbeat/OTP faults, and probe/remove reporter lifecycle. No executable tests were run for this research item.
