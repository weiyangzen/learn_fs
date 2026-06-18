# sources/distributed-fs/ceph-client/sound/soc/codecs/cs-amp-lib-test.c

## Purpose
This file is the KUnit test suite for `cs-amp-lib.c`, the Cirrus Logic smart-amplifier helper library. It validates firmware calibration coefficient access, EFI calibration read/write behavior, vendor speaker ID detection, Dell SSIDExV2 variant parsing, and the KUnit static-stub hook surface exported by the library.

## Important APIs, types, and functions
The suite private state is `struct cs_amp_lib_test_priv`, which owns a faux amp device, a mutable fake `struct cirrus_amp_efi_data` blob, a list of fake firmware-control writes, and captured EFI attributes. `struct cs_amp_lib_test_param` drives parameterized tests over amplifier counts, indices, and vendor strings. Static-stub replacements simulate EFI get/set calls, firmware coefficient reads/writes, write-protected EFI storage, zero-filled BIOS-reserved blobs, HP/Cirrus calibration variables, Lenovo and HP speaker-ID variables, and Dell SSIDExV2 variables.

The tested library APIs are `cs_amp_get_efi_calibration_data()`, `cs_amp_set_efi_calibration_data()`, `cs_amp_write_cal_coeffs()`, `cs_amp_read_cal_coeffs()`, `cs_amp_write_ambient_temp()`, `cs_amp_get_vendor_spkid()`, and `cs_amp_devm_get_vendor_specific_variant_id()`. `cs_amp_lib_test_case_init()` creates per-test state and a faux device. `cs_amp_lib_test_cases[]` lists all KUnit cases, and `kunit_test_suite(cs_amp_lib_test_suite)` registers the suite as `snd-soc-cs-amp-lib-test`.

## Control flow
Each test initializes private state, activates static stubs, invokes a public library API, and checks returned errors plus mutated fake state. Calibration read tests cover truncated headers, declared counts larger than the file, missing variables, HP variable preference, UID lookup, unchecked index lookup, UID-checked fallback to index, zero UID handling, out-of-range index handling, and ignored entries whose timestamp is zero.

Firmware coefficient tests verify that calibration writes emit ambient, calR, status, and checksum controls in order, that reads populate ambient/calR/status plus a non-zero timestamp, and that ambient-only writes touch only the ambient control. EFI write tests cover creating a new variable, indexed placement, unspecified maximum size, appending while growing, writing into zero-filled preallocated EFI space without shrinking it, replacing by index or UID, deduplicating duplicate calibration targets by clearing timestamps, finding empty slots, rejecting zero calTarget writes, preserving EFI attributes, respecting HP vendor-variable updates, and preserving old fake storage when writes are denied.

Speaker-ID tests simulate absent, valid, invalid, and oversize Lenovo/HP EFI byte variables. Dell variant tests parse valid SSIDExV2 strings, reject invalid second fields, reject non-Dell callers, and report `-ENOENT` when no variant variable exists.

## State and persistence behavior
The suite has no durable state. It models EFI persistence with an in-memory `cal_blob` that fake `set_efi_variable` replaces after successful writes. Empty calibration entries are represented by zeroing both `calTime` words. The faux device is created per test and destroyed through a KUnit action. Randomized calibration payloads exercise copy/replace behavior while assertions focus on structural invariants.

## Dependencies and integration points
The test depends on KUnit, KUnit static stubs, faux devices, kernel list helpers, random bytes, EFI GUID/status definitions, Cirrus DSP/control structures, and `<sound/cs-amp-lib.h>`. It imports the `SND_SOC_CS_AMP_LIB` namespace and requires `CONFIG_SND_SOC_CS_AMP_LIB_TEST_HOOKS` so `cs_amp_test_hooks` is non-null and the library redirects static helper calls. It is the primary in-tree test signal for the EFI calibration code in `cs-amp-lib.c`.

## Risks and test signals
The suite gives strong coverage for calibration storage edge cases, but it does not exercise real EFI runtime services, real cs_dsp firmware controls, concurrent writers contending on the library mutex, debugfs creation, or full integration with an actual ASoC amplifier driver. Passing this suite is a high-signal indication that calibration lookup/update semantics, UID/index behavior, vendor variable preference, and speaker/variant parsing remain compatible with the library contract.
