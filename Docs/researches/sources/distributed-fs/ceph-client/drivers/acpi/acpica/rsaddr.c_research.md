# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsaddr.c

Purpose: implements the conversion metadata and common helpers for ACPI address resource descriptors: `Address16`, `Address32`, `Address64`, and `ExtendedAddress64`. It is part of the ACPICA resource manager's table-driven AML-to-internal-resource and internal-resource-to-AML conversion path.

Important APIs, types, and functions: the exported data symbols are `acpi_rs_convert_address16`, `acpi_rs_convert_address32`, `acpi_rs_convert_address64`, and `acpi_rs_convert_ext_address64`, each a `struct acpi_rsconvert_info` conversion table. The local flag tables `acpi_rs_convert_general_flags`, `acpi_rs_convert_mem_flags`, and `acpi_rs_convert_io_flags` describe bit extraction/insertion for common, memory-specific, and I/O-specific address flags. `acpi_rs_get_address_common()` validates the AML resource type and imports common/type-specific flags; `acpi_rs_set_address_common()` writes the same fields back to AML.

Control flow: descriptor-specific conversion begins with `ACPI_RSC_INITGET`/`ACPI_RSC_INITSET`, invokes `ACPI_RSC_ADDRESS` for common flags, moves contiguous granularity/min/max/translation/length fields at the correct integer width, and optionally handles `resource_source`. The common getter rejects resource types greater than `2` unless they are vendor-defined `>= 0xC0` or the known value `0x0A`; memory and I/O ranges are decoded through specific flag tables, while bus/generic ranges preserve the raw `type_specific` byte.

State and persistence: this file holds static conversion tables only and mutates caller-provided AML/resource buffers during conversion. There is no independent persistent state.

Dependencies and integration points: depends on `acresrc.h` conversion opcodes, `union aml_resource`, `struct acpi_resource`, and dispatch from `rsinfo.c`. `rsmisc.c` interprets these tables, while `rsxface.c`, `rscreate.c`, and `rsutils.c` expose/use the converted resources for `_CRS`, `_PRS`, `_SRS`, and address normalization.

Risks and test signals: correctness depends on structure offsets matching ACPICA ABI layouts and AML descriptor definitions. Bad flag bit positions or width moves can corrupt PCI/root-bus windows, memory apertures, or I/O decode semantics. Boundary tests should round-trip address descriptors with memory, I/O, bus, vendor-defined, optional `resource_source`, and extended address type-specific attributes, plus reject invalid AML resource type values.
