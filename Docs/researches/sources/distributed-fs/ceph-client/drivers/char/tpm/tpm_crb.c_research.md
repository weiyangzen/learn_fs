<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c

## Purpose
Implements the ACPI TPM 2.0 Command Response Buffer driver, including memory mapping, locality control, command ready/idle sequencing, command start/cancel methods, Pluton support, ARM SMC, and Arm FF-A start integration.

## Important APIs, Types, And Functions
Important types include `struct crb_regs_head`, `struct crb_regs_tail`, `struct crb_priv`, `struct tpm2_crb_smc`, `struct tpm2_crb_ffa`, and `struct tpm2_crb_pluton`. Key functions are `tpm_crb_has_idle()`, `crb_wait_for_reg_32()`, `crb_try_pluton_doorbell()`, `__crb_go_idle()`, `__crb_cmd_ready()`, locality request/relinquish helpers, `crb_status()`, `crb_recv()`, `crb_send()`, `crb_cancel()`, `crb_map_io()`, `crb_map_pluton()`, `crb_acpi_probe()`, and `crb_acpi_remove()`.

## Control Flow
ACPI probe reads the `TPM2` table, rejects FIFO-handled memory-mapped start method, parses start-method-specific parameter blocks, initializes FF-A if needed, maps Pluton doorbells when present, maps CRB control/command/response regions from ACPI resources, requests locality, wakes the device, reads command/response buffer addresses and sizes, maps buffers, releases locality, allocates a TPM2 chip, bootstraps it, applies AMD hwrng disable quirk, and registers it. Send clears cancel, copies the command to the mapped buffer, issues the appropriate CRB/ACPI/SMC/FF-A/Pluton start method, and returns for generic polling. Receive validates error status and response length before copying from the response buffer.

## State And Persistence
`struct crb_priv` persists mapped register pointers, command/response buffers, command size, start method, ACPI HID, SMC function ID, Pluton doorbells, and FF-A metadata. TPM chip flags mark TPM2 and may disable hwrng for selected AMD systems.

## Dependencies And Integration Points
Integrates ACPI TPM2 tables/resources, platform driver matching `MSFT0101`, TPM core class ops, PM suspend/resume, memory-mapped I/O, optional ARM SMCCC, optional CRB FF-A helper, x86 CPU vendor quirk data, and TPM2 bootstrap.

## Risks And Edge Cases
Firmware ACPI resource descriptions are frequently inconsistent; `crb_fixup_cmd_size()` trusts the ACPI region over register size. Start-method handling differs for ACPI start, memory-mapped CRB, ARM SMC, FF-A, Pluton, and Intel PTT quirked MSFT0101 devices. Locality and idle transitions can time out. Response length and overlapping command/response buffer sizes must be validated.

## Test Signals
Boot CRB TPM2 systems using each start method, malformed ACPI table/resource tests, command/response buffer overlap and truncation cases, Pluton doorbell completion, ARM SMC/FF-A start paths, cancellation, suspend/resume, AMD hwrng quirk, and securityfs/char-device command traffic after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb.c -->
