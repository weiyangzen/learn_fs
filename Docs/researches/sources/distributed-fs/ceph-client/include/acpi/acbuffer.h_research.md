<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acbuffer.h -->
# sources/distributed-fs/ceph-client/include/acpi/acbuffer.h

## Purpose
`acbuffer.h` defines ACPICA's C representations for buffers returned by ACPI predefined names, especially `_FDE`, `_GRT`, `_GTM`, and `_PLD`, plus the `_SRT` time-setting payload. It also defines bit extraction and construction macros for the packed `_PLD` buffer format without relying on compiler-dependent C bitfield layout.

## Important APIs, types, and functions
The important exported types are `struct acpi_fde_info`, `struct acpi_grt_info`, `struct acpi_gtm_info`, and `struct acpi_pld_info`. `_PLD` support includes `ACPI_PLD_REV1_BUFFER_SIZE`, `ACPI_PLD_REV2_BUFFER_SIZE`, `ACPI_PLD_BUFFER_SIZE`, and `ACPI_PLD_GET_*`/`ACPI_PLD_SET_*` macros for revision, color, geometry, visibility, dock/lid/panel position, shape, group metadata, ejectability, cabinet/card cage, rotation/order, and revision-2 offsets. Panel constants such as `ACPI_PLD_PANEL_TOP` through `ACPI_PLD_PANEL_UNKNOWN` encode standard ACPI panel positions.

## Control flow
This header has no executable control flow. Runtime parsing happens in ACPICA interfaces such as `acpi_decode_pld_buffer`, which consumes raw AML buffer bytes and fills `struct acpi_pld_info` using these macros. Firmware construction paths may use the corresponding setters.

## State and persistence behavior
There is no owned state. The structures are transient decoded views over firmware-provided ACPI method buffers. Persistence is external: AML methods return the raw buffers and ACPICA/kernel callers allocate and free decoded results.

## Dependencies and integration points
The macros depend on bit helpers and integer masks from ACPICA core headers such as `actypes.h`. `acpixf.h` includes this file because `acpi_decode_pld_buffer()` exposes `struct acpi_pld_info`. Linux ACPI device-location helpers in `acpi_bus.h` consume the decoded `_PLD` information for physical placement and user-visible device metadata.

## Risks and test signals
Risks are mostly ABI and firmware-data risks: wrong byte ordering, incorrect revision-1 versus revision-2 length handling, field-offset drift against the ACPI specification, and callers assuming C structure packing mirrors the raw `_PLD` buffer. Test signals include decoding 16-byte and 20-byte `_PLD` buffers, validating color-ignore behavior, checking panel/position constants against known firmware, fuzzing short buffers, and round-tripping getter/setter macros on each documented bit range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acbuffer.h -->
