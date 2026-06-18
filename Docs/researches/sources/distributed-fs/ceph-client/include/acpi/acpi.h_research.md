<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi.h

## Purpose
`acpi.h` is the master public ACPICA include for code that interfaces with the ACPI Component Architecture. It provides a stable include order for environment definitions, names, types, exceptions, table layouts, resource descriptors, diagnostics, OS services, and public ACPICA functions.

## Important APIs, types, and functions
This file exports no independent APIs. Its important behavior is the include sequence: `platform/acenv.h`, `acnames.h`, `actypes.h`, `acexcep.h`, `actbl.h`, `acrestyp.h`, `platform/acenvex.h`, `acoutput.h`, `acpiosxf.h`, and `acpixf.h`. The order matters because later headers depend on environment macros, core typedefs, exception codes, table structures, and diagnostic definitions.

## Control flow
There is no runtime control flow. Compile-time inclusion through this file determines which declarations and macros a translation unit sees and prevents subtle ordering defects that would occur if ACPICA headers were included ad hoc.

## State and persistence behavior
No state is created. The included headers declare globals and structures used elsewhere, but `acpi.h` is only an aggregation point.

## Dependencies and integration points
Kernel ACPI code and ACPICA implementation files include this when they need the full public surface. It ties together ACPICA's OS-independent layer with Linux-specific platform headers and OSL implementations. Because it includes table definitions, resource definitions, and external interfaces, it is a high-fanout dependency.

## Risks and test signals
Risks include include-order regressions, accidental removal of a dependency that downstream files rely on, increased compile blast radius, and macro namespace collisions. Test signals include full kernel ACPI builds, standalone ACPICA tool builds, compile tests for files that include only `acpi.h`, and header self-containment checks under different platform configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi.h -->
