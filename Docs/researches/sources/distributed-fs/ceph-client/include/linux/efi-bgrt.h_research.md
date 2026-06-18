# sources/distributed-fs/ceph-client/include/linux/efi-bgrt.h

## Purpose
This header declares ACPI BGRT support for EFI boot graphics resource table handling. It exposes initialization/parsing hooks and the parsed BGRT image metadata when enabled.

## Important APIs, types, and functions
When `CONFIG_ACPI_BGRT` is enabled, APIs are `efi_bgrt_init(struct acpi_table_header *table)` and `acpi_parse_bgrt(struct acpi_table_header *table)`. Extern data are `bgrt_image_size` and `bgrt_tab`. When disabled, both functions are inline no-ops returning success for parse.

## Control flow, state, and persistence
The implementation parses an ACPI BGRT table during boot and stores the image size and table data globally. The data is valid only if the underlying BGRT image exists, as noted by the header comment.

## Dependencies and integration points
It depends on ACPI table definitions and integrates with EFI firmware boot logo/resource handling and ACPI table parsing.

## Risks and test signals
Risks include malformed ACPI tables, stale image pointers, disabled-config no-op behavior hiding missing support, and boot-time memory lifetime issues. Tests should cover valid and invalid BGRT parsing, disabled-config stubs, image-size reporting, and use only after a valid BGRT image is present.
