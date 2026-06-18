# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utcksum.c

Purpose: `utcksum.c` verifies and generates ACPI 8-bit circular checksums for standard tables and CDAT-like tables.

Important APIs/types/functions: `acpi_ut_verify_checksum()` skips FACS/S3PT, computes the correct standard-table checksum, warns on mismatch, and optionally aborts under `ACPI_CHECKSUM_ABORT`. `acpi_ut_verify_cdat_checksum()` handles CDAT length/checksum fields. `acpi_ut_generate_checksum()` computes the byte needed to make the table sum zero after excluding the original checksum byte. `acpi_ut_checksum()` returns the raw circular sum over a buffer.

Control flow: Verification uses the table's own length field rather than the incoming length parameter for standard ACPI tables. A mismatch emits BIOS warnings and may return `AE_BAD_CHECKSUM` depending on build policy. CDAT verification writes the computed checksum back into `cdat_table->checksum`.

State and persistence behavior: Standard verification does not mutate the table. CDAT verification mutates the checksum field. No global state is stored.

Dependencies and integration points: It is used by root table parsing, FADT parsing, table validation, RSDP validation, and disassembler/application paths. It depends on table signatures and ACPICA warning macros.

Risks and test signals: Risks include trusting corrupted length fields, optional abort policy differences, CDAT checksum assignment semantics, and skipping checksum for nonstandard tables. Tests should include valid/invalid checksums, FACS/S3PT skip, checksum byte regeneration, zero-length or truncated buffers at callers, and `ACPI_CHECKSUM_ABORT` builds.
