# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.c

## Purpose
`ath12k/acpi.c` implements ACPI DSM integration for ath12k. It discovers platform-provided capability bits and regulatory/power payloads, validates ACPI object types and sizes, stores them in `ab->acpi`, pushes enabled tables to firmware with WMI BIOS commands, handles ACPI notify updates for TAS/SAR data, and extracts BDF variant names for QMI firmware file selection.

## Important APIs, Types, And Functions
- `ath12k_acpi_dsm_get_data()` evaluates the hardware-specific DSM GUID/function and decodes integer, string, or buffer results into `ab->acpi`.
- `ath12k_acpi_start()` resets ACPI state, reads supported DSM functions, gathers disable flags, BDF extension, TAS config/data, BIOS SAR, GEO offset, CCA threshold, and band-edge power tables, derives enable booleans, and installs an ACPI notify handler.
- `ath12k_acpi_set_dsm_func()` sends enabled TAS, SAR/GEO, CCA, and band-edge payloads to firmware after WMI is available.
- `ath12k_acpi_dsm_notify()` refreshes TAS data and optionally BIOS SAR on ACPI notify.
- `ath12k_acpi_get_disable_rfkill()`, `ath12k_acpi_get_disable_11be()`, `ath12k_acpi_check_bdf_variant_name()`, and `ath12k_acpi_stop()` expose cached platform state to the rest of the driver.

## Control Flow And State Behavior
Startup is conservative. If the hardware lacks `acpi_guid`, the function returns success without enabling ACPI. Otherwise it reads the function bitmap and conditionally evaluates each supported DSM function. Every buffer payload is size-checked against constants before copying. Version and enable bytes are then inspected to set `acpi_tas_enable`, `acpi_bios_sar_enable`, `acpi_cca_enable`, `acpi_band_edge_enable`, and `acpi_enable_bdf`.

The driver stores ACPI state in `ab->acpi`; there is no persistent storage beyond firmware state after WMI commands are sent. `ath12k_acpi_stop()` removes the notify handler and zeroes the cached structure. Notify handling updates cached TAS/SAR tables and immediately re-sends firmware power limits if relevant.

## Dependencies And Integration Points
The file depends on Linux ACPI DSM APIs, ath12k core state, WMI BIOS command helpers, debug logging, and hardware parameters carrying the ACPI GUID. It integrates with QMI BDF selection through `ab->qmi.target.bdf_ext`, with firmware regulatory/power behavior through WMI, and with rfkill/11be capability policy through getter helpers.

## Risks And Edge Cases
- DSM object validation is central; accepting the wrong length would copy malformed firmware payloads.
- `ath12k_acpi_dsm_notify()` appears to treat `event == ATH12K_ACPI_NOTIFY_EVENT` as unknown and returns, so only other event values trigger refresh. That deserves hardware-level confirmation.
- `memcpy(ab->acpi.bdf_string, obj->string.pointer, obj->buffer.length)` is in the string branch and uses `obj->buffer.length`; if ACPI union layout does not alias as expected, this is a fragile field choice.
- BDF variant extraction skips four bytes from a string anchored by `"BDF"`, so malformed separators can affect firmware variant names.
- TAS takes precedence over BIOS SAR enablement; platforms providing both are intentionally routed through TAS unless TAS is invalid.

## Test Signals
Test no-ACPI GUID hardware, missing ACPI handle, integer and buffer support-function bitmaps, invalid buffer sizes for each DSM function, valid TAS/SAR/GEO/CCA/band-edge WMI handoff, notify-driven table update, BDF extension parsing, rfkill/11be disable flags, ACPI stop idempotence, and builds with `CONFIG_ACPI=n` using header stubs.
