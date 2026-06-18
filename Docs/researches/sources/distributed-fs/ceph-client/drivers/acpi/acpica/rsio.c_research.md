# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsio.c

Purpose: defines conversion tables for small I/O, fixed I/O, generic register, start/end dependent functions, and end tag resource descriptors.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_io`, `acpi_rs_convert_fixed_io`, `acpi_rs_convert_generic_reg`, `acpi_rs_convert_end_dpf`, `acpi_rs_convert_end_tag`, `acpi_rs_get_start_dpf`, and `acpi_rs_set_start_dpf`.

Control flow: the I/O and fixed I/O tables move decode flags, base/min/max/alignment/length fields, and generic register address-space metadata using fixed-width conversion opcodes. End-dependent and end-tag descriptors are minimal `INITGET`/`INITSET` tables. `StartDependentFn` has asymmetric get/set logic: get initializes default acceptable priorities, reads descriptor length from the small descriptor type byte, exits early if no flags byte is present, and otherwise decodes two 2-bit priority fields. Set starts with the one-byte form, can force or optimize to zero-length priority data, and only omits the flags byte when both priority values are `ACPI_ACCEPTABLE_CONFIGURATION`.

State and persistence: static conversion metadata only; conversion mutates caller buffers through `rsmisc.c`.

Dependencies and integration points: dispatch comes from `rsinfo.c`; table execution is in `rsmisc.c`; length planning is in `rscalc.c`. End tags are especially important because list walkers in `rscalc.c`, `rslist.c`, `rsdump.c`, and `rsxface.c` stop on them.

Risks and test signals: end-tag and zero-length dependent-function behavior affects resource-template termination and list walking. Start-dependent optimization has explicit TODO comments about validating incompatible flags for zero-byte descriptors. Tests should round-trip fixed and variable `StartDependentFn` descriptors, generic registers with 64-bit addresses, end tags, and missing end-tag error paths.
