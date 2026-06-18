## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utresrc.c

Purpose: `utresrc.c` validates and walks raw AML resource templates. It provides descriptor-size tables, resource type classification, and helpers for extracting descriptor type, payload length, header length, full descriptor length, and end tags.

Important APIs and data: `acpi_gbl_resource_aml_sizes[]` gives minimum/fixed AML payload sizes by resource index, including small and large descriptor forms. `acpi_gbl_resource_aml_serial_bus_sizes[]` covers serial bus subtypes. Static `acpi_gbl_resource_types[]` classifies descriptor lengths as fixed, variable, or small-variable. `acpi_ut_walk_aml_resources`, `acpi_ut_validate_resource`, `acpi_ut_get_resource_type`, `acpi_ut_get_resource_length`, `acpi_ut_get_resource_header_length`, `acpi_ut_get_descriptor_length`, and `acpi_ut_get_resource_end_tag` form the public utility surface.

Control flow: the walker first requires room for an end tag, then repeatedly validates the current descriptor, computes total length, invokes an optional callback, and stops when it finds an end tag. If no end tag is found and a callback exists, it injects a synthetic end tag callback before returning `AE_AML_NO_RESOURCE_END_TAG`.

State and dependencies: there is no mutable state. The code depends on AML resource structure definitions, ACPI move/get macros, and optional `walk_state` for error reporting.

Integration points: resource conversion, `_CRS`/`_PRS` parsing, ASL compiler checks, namespace repair paths, and resource dump/disassembly code rely on these helpers to avoid walking malformed buffers.

Risks: validation must reject invalid type/length combinations before using descriptor lengths for pointer advancement. SerialBus descriptors need subtype validation. The end-tag checksum byte is intentionally not validated for field compatibility.

Test signals: fixed-length mismatch, variable-length minimums, small IRQ min/min-minus-one forms, invalid large/small type values, invalid SerialBus type zero/out of range, missing/truncated end tags, zero-length resource buffer, and callback failure propagation should be covered.
