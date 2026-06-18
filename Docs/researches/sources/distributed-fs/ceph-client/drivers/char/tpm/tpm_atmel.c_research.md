<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c

## Purpose
Implements the legacy Atmel TPM 1.1 I/O-port/platform driver and registers it with the generic TPM core.

## Important APIs, Types, And Functions
Defines `struct tpm_atmel_priv`, register helpers `tpm_read_index()`, `atmel_verify_tpm11()`, `atmel_get_base_addr()`, TPM ops `tpm_atml_recv()`, `tpm_atml_send()`, `tpm_atml_cancel()`, `tpm_atml_status()`, `tpm_atml_req_canceled()`, lifecycle helpers `init_atmel()`, `cleanup_atmel()`, and `atml_plat_remove()`.

## Control Flow
Module init registers a platform driver, verifies Atmel vendor/version bytes through indexed I/O ports, reads the base address, maps two I/O ports, optionally reserves the region, creates a platform device, allocates private state and a TPM chip, and registers it. Send writes command bytes to the data port. Receive reads the six-byte header and payload while checking `DATA_AVAIL`, validates response size, and ensures data availability clears. Cancel writes the abort bit.

## State And Persistence
The global `pdev` persists the created platform device. Per-chip private state stores region ownership, base port, region size, and mapped I/O base. The TPM core owns device registration, sysfs, and char-device state.

## Dependencies And Integration Points
Depends on legacy x86-style I/O port access, `ioport_map()`, platform device/driver APIs, TPM core registration, and generic TPM PM helpers.

## Risks And Edge Cases
The driver reserves the region only opportunistically and records whether it succeeded. Probe is legacy and global rather than firmware-enumerated. Receive must drain or detect leftover data on size errors. Cleanup order depends on `pdev` existing after init success.

## Test Signals
Legacy Atmel hardware probe, vendor/version rejection, region reservation failure/success, command send/receive, malformed response sizes, cancel behavior, suspend/resume, and module unload after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_atmel.c -->
