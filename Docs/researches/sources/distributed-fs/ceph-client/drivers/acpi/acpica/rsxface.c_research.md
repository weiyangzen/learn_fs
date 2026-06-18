# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsxface.c

Purpose: exposes ACPICA public resource-manager interfaces used by OS code and drivers to get, set, convert, search, and walk ACPI resources.

Important APIs, types, and functions: exported APIs include `acpi_get_irq_routing_table()`, `acpi_get_current_resources()`, `acpi_get_possible_resources()`, `acpi_set_current_resources()`, `acpi_get_event_resources()`, `acpi_resource_to_address64()`, `acpi_get_vendor_resource()`, `acpi_walk_resource_buffer()`, and `acpi_walk_resources()`. Internal helpers are `acpi_rs_validate_parameters()` and `acpi_rs_match_vendor_resource()`.

Control flow: common validation requires a non-null handle, a namespace node of type `ACPI_TYPE_DEVICE`, and a valid `struct acpi_buffer`. Getters then call `rsutils.c` helpers for `_PRT`, `_CRS`, `_PRS`, or `_AEI`; setter rejects empty input and calls `_SRS`. `acpi_resource_to_address64()` copies 16/32/64-bit address resource fields into a uniform 64-bit output. Vendor resource lookup walks a named resource method and copies the first vendor descriptor whose subtype and 16-byte UUID match. Resource walkers validate buffer/user callback, iterate until buffer end or `END_TAG`, reject invalid/zero-length descriptors, and treat `AE_CTRL_TERMINATE` from callbacks as successful early termination.

State and persistence: no global state is owned. APIs allocate local buffers through downstream helpers and free them after walking. `acpi_set_current_resources()` can persist device configuration by invoking firmware `_SRS`.

Dependencies and integration points: this is the external interface layer over `rsutils.c`, `rscreate.c`, and `rslist.c`. It is exported to the kernel/ACPICA integration through `ACPI_EXPORT_SYMBOL`.

Risks and test signals: public API validation must prevent non-device handles and bad buffers from reaching namespace execution. Walkers must not loop on zero-length resources. Vendor resource matching assumes typed vendor data layout. Tests should cover each exported API's parameter validation, buffer sizing semantics, `_CRS`/`_PRS`/`_AEI` walking, callback early termination, address conversion for all supported widths, and `_SRS` invocation with invalid and valid lists.
