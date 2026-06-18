# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ppi.c

## Purpose
Adds the ACPI Physical Presence Interface sysfs group under TPM devices, exposing firmware-mediated TPM operation requests, responses, transition actions, and supported operation policy.

## Important APIs, Types, And Functions
The public entry point is `tpm_add_ppi()`. Sysfs handlers include version, request show/store, transition action, response, TCG operations, and vendor-specific operations. `tpm_eval_dsm()` wraps ACPI DSM evaluation, and `cache_ppi_operations()` fills a global operation cache protected by `tpm_ppi_lock`.

## Control Flow
`tpm_add_ppi()` checks for an ACPI handle and PPI DSM version function, caches the firmware version string, and appends the `ppi` attribute group to the TPM chip. Request show calls DSM GETREQ and supports two- or three-integer packages, printing parameterized request 23 specially. Request store chooses SUBREQ or SUBREQ2, formats argv4 differently for PPI version compatibility, evaluates DSM, and maps firmware return codes. Operation show paths lazily cache GETOPR results for request ids 0..255 and print human-readable policy strings.

## State And Persistence
The kernel caches the PPI version in `chip->ppi_version` and operation policies in global `ppi_operations_cache`. Submitted requests and responses persist in firmware/BIOS variables outside the driver.

## Dependencies And Integration Points
Depends on ACPI DSM GUID `3DDDFAA6-361B-4EB4-A424-8D10089D1653`, TPM chip ACPI handles, sysfs attribute groups, and firmware PPI versions 1.0 through 1.3.

## Risks And Edge Cases
Firmware returns vary widely, so handlers accept legacy buffer/package argument forms. The operation cache is global, not per-chip, which can be wrong on systems with multiple TPM ACPI handles. Sysfs buffers can be filled with many operation lines, so bounds rely on `sysfs_emit_at()`.

## Test Signals
PPI versions 1.0, 1.1, 1.2, and 1.3; request 23 with parameter; malformed DSM packages; denied and BIOS-failure responses; operation cache population; absence of PPI DSM; and multi-TPM ACPI scenarios.
