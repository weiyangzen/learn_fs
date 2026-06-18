<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c

## Purpose
Repairs common invalid objects returned by predefined ACPI methods so ACPICA clients receive spec-compatible values despite firmware defects.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_simple_repair`, `acpi_ns_repair_null_element`, `acpi_ns_remove_null_elements`, and `acpi_ns_wrap_with_package`, plus the repair dispatch table `acpi_object_repair_info`. It uses converter functions from `nsconvert.c`, expected return bitmaps, package indexes, and `ACPI_OBJECT_REPAIRED`/`ACPI_OBJECT_WRAPPED` flags.

## Control Flow
Simple repair first checks name-specific conversions: resource-return names (`_CRS`, `_DMA`, `_PRS`) can become end-tag resource buffers; `_DEP` strings become references; `_MLS` and `_STR` strings become Unicode buffers. If returned type is already expected it succeeds. Missing package elements can be repaired to zero integer, empty string, or empty buffer. Otherwise it tries conversions to expected integer, string, buffer, or wraps a lone object in a package. Successful scalar repair replaces the old object and removes its reference; package-element repair preserves parent package reference count. Null removal compacts variable package element arrays and updates count. Wrapping creates a one-element outer package around the original object.

## State And Persistence
Mutates return object pointers, package elements/counts, object reference counts, and evaluation return flags. It does not alter namespace nodes directly except through caller-visible repaired returns.

## Dependencies And Integration Points
Used by `nspredef.c` and `nsprepkg.c`. Depends on conversion helpers, predefined method names, package metadata, reference-count utilities, and repair debug logging.

## Risks And Edge Cases
Repair is intentionally permissive and can hide BIOS bugs. Reference-count transfer differs for wrapped objects versus converted package elements. Null removal is safe only for selected variable package types. Missing top-level returns are not generally fabricated unless a name-specific repair allows it.

## Test Signals
Exercise resource null/zero/empty repairs, `_DEP` string paths, `_STR`/`_MLS` Unicode conversion, scalar type conversions, NULL package element replacement, variable-package null compaction, object wrapping, repair-disabled mode, and reference-count leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair.c -->
