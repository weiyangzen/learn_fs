# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.c

## Purpose
ACPI thermal relationship helper and misc character device. It parses ACPI `_TRT`, `_ART`, and `PSVT` relationship tables for in-kernel consumers and exposes them to userspace through ioctl calls on `acpi_thermal_rel`.

## Important APIs, Types, and Functions
- Global `acpi_thermal_rel_handle` points to the ACPI device containing relationship tables.
- `acpi_thermal_rel_open()`/`release()` implement simple exclusive-open handling under a spinlock.
- Exported parsers `acpi_parse_trt()` and `acpi_parse_art()` evaluate ACPI methods, extract package entries, optionally instantiate referenced ACPI devices, skip malformed entries, and return allocated arrays.
- Static `acpi_parse_psvt()` parses version-2 `PSVT`, supports integer or string control-knob limit fields, validates source/target devices, and returns allocated entries.
- `get_single_name()` converts ACPI handles to 4-character names for userspace payloads.
- `fill_trt()`, `fill_art()`, and `fill_psvt()` convert parsed kernel structures into user ABI unions and copy them to userspace.
- `acpi_thermal_rel_ioctl()` handles count, length, and data ioctls for TRT/ART/PSVT.
- `acpi_thermal_rel_misc_device_add()` and `_remove()` register/deregister the misc device and are exported.

## Control Flow
INT3400 or another caller registers the misc device with an ACPI handle. Userspace opens the nonseekable char device, then issues ioctls. Count/length ioctls parse the relevant ACPI table and return a scalar. Data ioctls parse the table, allocate ABI-sized arrays, translate handles to ACPI single names, copy fields, and copy to userspace. Kernel drivers can call `acpi_parse_trt()`/`acpi_parse_art()` directly and free the returned arrays.

## State and Persistence
The misc device has global open count/exclusive state and a global ACPI handle. Parsed table data is allocated per call and freed by caller or fill helper. No table data is cached.

## Dependencies and Integration Points
Depends on ACPI evaluation/extraction, miscdevice, file operations, copy_to_user/put_user, platform ACPI device creation through `acpi_fetch_acpi_dev()`, and the ABI definitions in `acpi_thermal_rel.h`.

## Risks and Edge Cases
- The misc device/global handle design assumes one active relationship provider; multiple INT3400-like devices would overwrite the handle.
- `ACPI_THERMAL_GET_PSVT_LEN` computes `length` even if parse fails and only frees `psvts` on success.
- `fill_*` ioctls copy data to user buffers without a user-provided size, relying on callers to query length first.
- `acpi_parse_art()` subtracts one for revision without first checking package count; malformed empty packages are risky.
- PSVT string parsing truncates overlong strings and stores type info in a field the spec calls reserved.

## Test Signals
Tests should cover valid and malformed TRT/ART/PSVT packages, bad entry skipping and count adjustment, string vs integer PSVT limit, source/target ACPI device lookup failures, ioctl count/len/data behavior, exclusive open semantics, copy_to_user fault injection, and register/deregister lifecycle.
