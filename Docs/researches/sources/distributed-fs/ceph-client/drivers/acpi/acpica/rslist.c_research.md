# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rslist.c

Purpose: performs list-level conversion between AML resource byte streams and native `struct acpi_resource` lists by dispatching each descriptor to the table-driven converter.

Important APIs, types, and functions: `acpi_rs_convert_aml_to_resources()` is an `acpi_ut_walk_aml_resources()` callback that converts one AML descriptor and advances the output pointer. `acpi_rs_convert_resources_to_aml()` walks an internal resource list and writes AML descriptors to an output buffer.

Control flow: AML-to-resource conversion checks output alignment, chooses the correct conversion table from the normal get dispatch table or serial bus subtype table, errors on unsupported descriptors, calls `acpi_rs_convert_aml_to_resource()`, warns on zero output length, then advances with `ACPI_NEXT_RESOURCE()`. Resource-to-AML conversion loops until the planned AML buffer end, validates internal type and nonzero length, selects the set conversion table or serial bus subtype conversion table, calls `acpi_rs_convert_resource_to_aml()`, validates the newly emitted AML descriptor with `acpi_ut_validate_resource()`, returns success on `END_TAG`, and otherwise advances both AML and internal-resource pointers.

State and persistence: no owned state. It mutates caller-supplied output buffers and pointer context.

Dependencies and integration points: connects `rscreate.c` allocation/sizing to the conversion interpreter in `rsmisc.c`, dispatch metadata in `rsinfo.c`, AML validation helpers, and public walkers in `rsxface.c`.

Risks and test signals: this is a loop-safety boundary. Unsupported serial bus subtypes, invalid resource types, zero lengths, missing `END_TAG`, or a converter that emits invalid AML all stop the operation. Tests should assert no infinite loops on zero length, rejection of out-of-range types/subtypes, validation failures after conversion, and exact end-tag termination behavior.
