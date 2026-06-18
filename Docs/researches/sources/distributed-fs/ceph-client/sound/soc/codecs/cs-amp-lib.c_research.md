# sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib.c

## Purpose
This file provides common helper code for Cirrus Logic smart amplifiers. It bridges amplifier drivers to firmware calibration controls, EFI-stored calibration blobs, vendor speaker identifiers, Dell variant strings, and a Cirrus-specific debugfs root.

## Important APIs, types, and functions
Public exported APIs are `cs_amp_write_cal_coeffs()`, `cs_amp_read_cal_coeffs()`, `cs_amp_write_ambient_temp()`, `cs_amp_get_efi_calibration_data()`, `cs_amp_set_efi_calibration_data()`, `cs_amp_get_vendor_spkid()`, `cs_amp_devm_get_vendor_specific_variant_id()`, `cs_amp_create_debugfs()`, and `cs_amp_test_hooks`. Internal firmware-control helpers are `cs_amp_write_cal_coeff()`, `cs_amp_read_cal_coeff()`, `_cs_amp_write_cal_coeffs()`, and `_cs_amp_read_cal_coeffs()`. EFI helpers include `cs_amp_get_efi_variable()`, `cs_amp_set_efi_variable()`, `cs_amp_convert_efi_status()`, `cs_amp_alloc_get_efi_variable()`, `cs_amp_get_cal_efi_buffer()`, `cs_amp_set_cal_efi_buffer()`, `_cs_amp_get_efi_calibration_data()`, and `_cs_amp_set_efi_calibration_data()`.

The file knows several EFI variables: Cirrus and HP calibration variables, Lenovo and HP one-byte speaker-ID variables, and Dell `SSIDexV2Data`. `cs_amp_efi_cal_write_lock` serializes calibration EFI updates. `cs_amp_test_hooks` exposes static helper entry points to KUnit when test hooks are enabled.

## Control flow
Firmware calibration writes first verify that DSP firmware controls exist, then write ambient, calR, status, and checksum (`calR + 1`) as big-endian control values under `dsp->pwr_lock`. Reads retrieve ambient, calR, and status, convert from big endian, and stamp the returned `cirrus_amp_cal_data` with current wall-clock time converted to Windows 100 ns time.

EFI calibration reads search the HP variable first and then the Cirrus variable. The code performs a size query, allocates a buffer, reads the variable, verifies the header and flexible-array count against the actual byte size, and treats a zero `size` header as BIOS-preallocated storage whose size is the EFI variable size. Lookup prefers a non-empty entry with non-zero calTarget matching `target_uid`; if none is found, a valid `amp_index` can return an entry whose calTarget is zero or when target matching is intentionally disabled.

EFI calibration writes reject zero calTarget, read the existing HP or Cirrus variable if present, create the Cirrus variable if none exists, initialize zero-filled preallocated blobs, choose a slot by explicit index, matching target, first empty entry, or array growth, deduplicate other active entries with the same calTarget when an explicit index is used, then write the resized blob back with preserved EFI attributes. The public setter wraps the update in `cs_amp_efi_cal_write_lock`.

Speaker ID lookup checks vendor byte variables in order and maps Lenovo `0xd0/0xd1` or HP `0x30/0x31` to speaker IDs 0/1. Dell variant lookup reads `SSIDexV2Data`, parses underscore-delimited fields, and returns a devm-managed two-character audio hardware ID only for Dell or unknown PCI vendor callers.

## State and persistence behavior
DSP coefficient state lives in firmware controls and is not durable by this file. EFI calibration data is durable platform firmware state and is written through EFI runtime services when available. The code preserves EFI attributes from an existing variable and uses nonvolatile boot/runtime access defaults for newly created Cirrus variables. Empty calibration slots are represented by zero `calTime`; calTarget must be non-zero for writes. Debugfs state is the `cirrus_logic/<dev_name>` directory created under the global debugfs root.

## Dependencies and integration points
The library depends on `FW_CS_DSP` for real DSP coefficient access, EFI runtime services for persistent calibration and vendor IDs, PCI vendor IDs for Dell gating, debugfs, KUnit static stubs, and public data structures from `<sound/cs-amp-lib.h>`. It exports symbols in namespace `SND_SOC_CS_AMP_LIB` and imports `FW_CS_DSP`. Consumer amplifier drivers pass their `struct cs_dsp`, `struct cirrus_amp_cal_controls`, silicon UID, amp index, and optional PCI SSID details.

## Risks and test signals
Risks include corrupt EFI variable layouts, firmware-reserved zero-filled buffers, target UID collisions, write failures after in-memory mutation, EFI runtime unavailability, endian mistakes in DSP controls, and concurrent writers racing without the global mutex. The current implementation reads the entire calibration variable into memory and bounds count at 128, limiting malformed flexible-array damage. High-value test signals are the KUnit suite in `cs-amp-lib-test.c`, real platform EFI read/write tests on HP and Cirrus variable names, speaker-ID detection on Lenovo/HP systems, Dell SSIDExV2 parsing, DSP firmware-control read/write smoke tests, and verification that failed EFI writes do not corrupt persistent calibration.
