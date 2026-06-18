# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscreate.c

Purpose: creates caller-visible ACPICA resource objects from AML buffers or namespace method results, and creates AML resource byte streams from internal resource lists for `_SRS`.

Important APIs, types, and functions: `acpi_buffer_to_resource()` is exported and converts a raw AML buffer into an allocated `struct acpi_resource` list. `acpi_rs_create_resource_list()` converts an evaluated `_CRS`, `_PRS`, `_AEI`, or similar buffer object into a caller-supplied `struct acpi_buffer`. `acpi_rs_create_pci_routing_table()` flattens `_PRT` packages into `struct acpi_pci_routing_table` entries. `acpi_rs_create_aml_resources()` converts an internal resource list to AML.

Control flow: raw AML conversion first calls `acpi_rs_get_list_length()`, allocates or initializes a buffer, then walks AML with `acpi_ut_walk_aml_resources()` and `acpi_rs_convert_aml_to_resources()`. `acpi_buffer_to_resource()` specifically tolerates `AE_AML_NO_RESOURCE_END_TAG`, while method-based list creation expects the normal resource-template end tag. `_PRT` creation sizes the output, iterates subpackages of exactly four elements, validates address/pin/source/source-index types, copies strings or resolves namespace references to pathnames, aligns each entry length, and leaves a final zeroed terminator. AML creation uses `acpi_rs_get_aml_length()`, initializes the caller buffer, then calls `acpi_rs_convert_resources_to_aml()`.

State and persistence: allocates transient buffers via ACPICA allocation helpers and fills caller buffers. It does not own persistent state but does transfer allocated memory ownership to callers on success.

Dependencies and integration points: sits between method evaluation helpers in `rsutils.c`, public APIs in `rsxface.c`, length calculation in `rscalc.c`, conversion walking in `rslist.c`, and namespace path helpers for `_PRT`.

Risks and test signals: error-path cleanup is important because conversion failures after allocation must not leak. `_PRT` parsing is type-sensitive and must preserve alignment for consumer iteration. Tests should cover buffer-overflow sizing behavior, local-buffer allocation, no-end-tag raw buffer tolerance, conversion failures, `_PRT` malformed packages, reference-to-path conversion, integer null sources, and AML round-trips for `_SRS` inputs.
