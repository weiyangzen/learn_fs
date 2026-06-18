# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/acpi_thermal_rel.h

## Purpose
Header defining the ACPI thermal relationship ioctl ABI and in-kernel data structures for ART, TRT, and PSVT thermal relationship tables.

## Important APIs, Types, and Functions
- Ioctl numbers: `ACPI_THERMAL_GET_TRT_LEN`, `GET_ART_LEN`, `GET_TRT_COUNT`, `GET_ART_COUNT`, `GET_TRT`, `GET_ART`, `GET_PSVT_LEN`, `GET_PSVT_COUNT`, and `GET_PSVT`.
- Kernel structs `struct art`, `struct trt`, and `struct psvt` mirror parsed ACPI table entries with ACPI handles and numeric fields.
- User ABI unions `union art_object`, `union trt_object`, and `union psvt_object` replace handles with 8-byte source/target name fields and expose fixed-size u64 layouts.
- Kernel prototypes expose misc-device registration and ART/TRT parsers.

## Control Flow
The header is included by the relationship driver and INT3400 thermal code. Userspace ioctl command numbers must match the char-device implementation. Kernel users call parser prototypes when `__KERNEL__` is defined.

## State and Persistence
No state. It defines packed layouts and ioctl constants that form a persistent ABI.

## Dependencies and Integration Points
Depends on ACPI handle types, `asm/ioctl.h`, and the misc-device implementation. The struct layouts are coupled to ACPI method package formats and userspace thermal daemons.

## Risks and Edge Cases
- ABI layout changes would break userspace; unions intentionally expose fixed u64 arrays.
- `ACPI_LIMIT_STR_MAX_LEN` is 8, so string limits are short and must be truncated consistently.
- `control_knob_type` borrows a reserved PSVT field for type metadata.
- Comment typo "usrspace" is harmless but signals old ABI surface.

## Test Signals
Compile tests should validate header inclusion in kernel and userspace-style contexts. ABI tests should check structure sizes, ioctl numbers, packed layout, and compatibility with `acpi_thermal_rel.c` copy logic.
