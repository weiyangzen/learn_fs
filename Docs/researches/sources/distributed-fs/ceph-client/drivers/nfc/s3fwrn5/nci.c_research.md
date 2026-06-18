# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.c

## Purpose
`nci.c` implements S3FWRN5 proprietary NCI operations, mainly RF-register configuration after firmware update.

## Important APIs, types, and functions
- `s3fwrn5_nci_prop_ops` registers response handlers for proprietary commands `SET_RFREG`, `START_RFREG`, `STOP_RFREG`, and `FW_CFG`.
- `s3fwrn5_nci_prop_rsp()` completes an NCI request with the returned status byte.
- `s3fwrn5_nci_rf_configure()` loads an RF register firmware file, computes a checksum, sends default clock config, starts RF-reg update, sends 252-byte chunks with incrementing index, and stops with checksum.

## Control flow
The shared core calls `s3fwrn5_nci_rf_configure()` after a successful firmware download and a switch back to NCI mode. The function requests `sec_s3fwrn5_rfreg.bin`, sends `FW_CFG`, then `START_RFREG`, multiple `SET_RFREG` commands, and finally `STOP_RFREG`. Each command is synchronous through `nci_prop_cmd()` and uses the proprietary response ops to complete.

## State and persistence
The RF-reg blob is external persistent input read through Linux firmware APIs. Driver state is temporary: checksum, chunk index, and stack command structs. No data is persisted by the driver.

## Dependencies and integration points
The file depends on NCI proprietary command support, firmware loader, and `struct s3fwrn5_info`. It is wired into `s3fwrn5_nci_ops` from `core.c`.

## Risks
Checksum loops in 4-byte increments over `fw->size` and casts firmware data to `u32 *`, so unaligned or non-multiple-of-four firmware sizes are risky. Chunk payload uses a fixed 252-byte buffer and sends `len + 1`; malformed or zero-length RF-reg files should be tested. Clock defaults are hard-coded for external crystal.

## Test signals
Test missing RF-reg file, short/non-multiple-of-four RF-reg file, command failure at each stage, checksum correctness, final release of firmware, and successful configuration after firmware update.
