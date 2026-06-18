# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/core.c

## Purpose
`core.c` is the shared Samsung S3FWRN5 NCI glue layer. It allocates/registers the NCI device, exposes common probe/remove entry points for physical layers, routes inbound frames to NCI or firmware-update handlers by mode, and performs post-setup firmware/RF-reg updates.

## Important APIs, types, and functions
- `s3fwrn5_probe()` and `s3fwrn5_remove()` are exported for I2C/UART physical drivers.
- `s3fwrn5_nci_ops` implements NCI `open`, `close`, `send`, and `post_setup`, plus proprietary RF-reg ops from `nci.c`.
- `s3fwrn5_nci_open()` transitions from COLD to NCI mode and asserts wake; `s3fwrn5_nci_close()` drops wake and returns to COLD.
- `s3fwrn5_nci_send()` serializes sends with `info->mutex`, rejects non-NCI mode, delegates to the physical `write`, and consumes/frees skb appropriately.
- `s3fwrn5_nci_post_setup()` optionally requests firmware, performs bootloader update, then resets and initializes the NCI core.
- `s3fwrn5_recv_frame()` dispatches inbound sk_buffs to `nci_recv_frame()` in NCI mode or `s3fwrn5_fw_recv_frame()` in firmware mode.

## Control flow
Physical-layer probe calls `s3fwrn5_probe()` with a `phy_id` and `s3fwrn5_phy_ops`. The core initializes mode COLD, allocates an NCI device supporting Jewel, MIFARE, Felica, ISO14443 A/B, and ISO15693, binds driver data, registers with NCI, and stores the NCI pointer back to the physical driver. After NCI setup, firmware init tries to load `sec_s3fwrn5_firmware.bin`; failure skips bootloader mode. If present, firmware mode is entered, boot info is read, versions are compared against `manufact_specific_info`, download may run, then NCI mode is used to push `sec_s3fwrn5_rfreg.bin` before a core reset/init.

## State and persistence
Runtime state is `struct s3fwrn5_info`: NCI device pointer, physical opaque id, device pointer, physical ops, firmware info, and a send mutex. Persistent inputs are external firmware files requested through the firmware loader; no driver state is written back to disk. Chip mode is delegated to physical ops and represented as COLD/NCI/FW.

## Dependencies and integration points
This file integrates with `net/nfc/nci_core.h`, firmware helpers, proprietary NCI RF-reg helpers, and physical transport implementations. It depends on physical layers honoring mode and wake semantics for safe bootloader/NCI transitions.

## Risks
Firmware request failure intentionally skips update, which may hide missing firmware deployment. `s3fwrn5_get_mode()` returns an enum but uses `-EOPNOTSUPP` if an op is missing; because the enum is unsigned-like logic, missing ops can produce confusing mode comparisons. Post-setup returns immediately if NCI reset fails after leaving wake asserted, so physical state cleanup on partial failure depends on later close/remove.

## Test signals
Tests should cover probe/register failure cleanup, open while not COLD returning `-EBUSY`, send rejection outside NCI mode, firmware absent path, firmware present but no update path, update plus RF-reg configuration path, and inbound frame routing in all three modes.
