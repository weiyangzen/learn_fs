# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmemory.c

Purpose: defines conversion tables for memory range descriptors and vendor-defined resource descriptors.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_memory24`, `acpi_rs_convert_memory32`, `acpi_rs_convert_fixed_memory32`, `acpi_rs_get_vendor_small`, `acpi_rs_get_vendor_large`, and `acpi_rs_set_vendor`.

Control flow: memory tables initialize the correct internal/external descriptor type, convert read/write protection, and move contiguous address fields at 16-bit or 32-bit width. Fixed memory moves base address and length. Vendor get tables use small or large AML header offsets, count vendor bytes from descriptor length, and copy byte data. Vendor set starts as a small vendor descriptor, copies byte data, exits when byte length is at most seven, and otherwise reinitializes as a large vendor descriptor and repeats length/data setup.

State and persistence: static conversion metadata only.

Dependencies and integration points: dispatched by `rsinfo.c`, executed by `rsmisc.c`, and sized by `rscalc.c`. Vendor resources are also searched by `acpi_get_vendor_resource()` in `rsxface.c`.

Risks and test signals: vendor small/large switching is a compatibility boundary because AML small descriptors can hold only seven data bytes. Incorrect counts can shift the variable data payload or misrepresent typed vendor UUID resources. Tests should round-trip memory24, memory32, fixed-memory32, zero-length vendor data, 1-7 byte small vendor data, 8+ byte large vendor data, and vendor UUID matching through `rsxface.c`.
