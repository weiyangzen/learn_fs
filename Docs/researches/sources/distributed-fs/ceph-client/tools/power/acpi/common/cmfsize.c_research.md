<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c

## Purpose
Contains the ACPICA utility helper `cm_get_file_size()`, which returns the byte length of an already-open `ACPI_FILE` without leaving the file positioned at EOF.

## Important APIs, Types, And Functions
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Control Flow
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## State And Persistence
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Dependencies And Integration Points
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Risks And Edge Cases
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Test Signals
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c -->
