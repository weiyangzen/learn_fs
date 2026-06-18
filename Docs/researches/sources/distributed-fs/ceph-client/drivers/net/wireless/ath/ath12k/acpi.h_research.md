# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.h

## Purpose
`ath12k/acpi.h` defines ACPI DSM function IDs, supported-function bits, payload versions, payload offsets/sizes, BDF string constraints, helper macros, and public ACPI integration declarations for ath12k. It also supplies compile-time stubs when `CONFIG_ACPI` is disabled.

## Important APIs, Types, And Constants
- DSM function IDs include support bitmap, disable flags, BDF extension, BIOS SAR, GEO offset, CCA index, TAS config/data, and band-edge data.
- Function bits mirror those DSM functions in `ab->acpi.func_bit`; disable bits currently cover 11be and rfkill policy.
- Size constants define fixed firmware payload contracts: TAS data/config, band-edge data, BIOS SAR plus GEO, CCA threshold, and BDF maximum length.
- `ATH12K_ACPI_FUNC_BIT_VALID()` and `ATH12K_ACPI_CHEK_BIT_VALID()` test cached function and disable bitmaps.
- Public APIs are `ath12k_acpi_start()`, `ath12k_acpi_stop()`, `ath12k_acpi_get_disable_rfkill()`, `ath12k_acpi_get_disable_11be()`, `ath12k_acpi_set_dsm_func()`, and `ath12k_acpi_check_bdf_variant_name()`.

## Control Flow And State Behavior
The header itself has no runtime flow. It defines the contract used by `acpi.c` to validate and slice DSM buffers before copying to `ab->acpi` or sending to firmware. With `CONFIG_ACPI=n`, start succeeds, stop and set are no-ops, feature getters return false, and BDF variant checking returns success without populating a variant.

## Dependencies And Integration Points
It includes `<linux/acpi.h>` and relies on `struct ath12k_base` from including contexts. The constants are coupled to firmware WMI BIOS command payloads and platform ACPI DSM methods identified by `ab->hw_params->acpi_guid`.

## Risks And Edge Cases
- Any size/offset mismatch with firmware or BIOS DSM layout can cause wrong power/regulatory data to be sent.
- The typo in `ATH12K_ACPI_CHEK_BIT_VALID` is API surface inside the driver; renaming requires coordinated source changes.
- Stubs must remain semantically safe for non-ACPI builds, especially getters returning false for disable flags.

## Test Signals
Compile with and without ACPI, verify every constant matches BIOS DSM documentation and `acpi.c` length checks, exercise bit macros with multi-byte support bitmaps, and confirm BDF string bounds reject overlong or unanchored values.
