# sources/distributed-fs/ceph-client/drivers/acpi/osi.c

`osi.c` implements Linux policy for ACPI `_OSI` strings. It queues command-line interface additions/removals, applies DMI and Apple/Darwin quirks, installs an ACPICA interface handler, and logs notable firmware `_OSI(Linux)` and `_OSI(Darwin)` queries.

Important elements are `struct acpi_osi_entry`, `struct acpi_osi_config`, `acpi_osi_setup()`, `osi_setup()` for `acpi_osi=`, `acpi_osi_setup_late()`, `acpi_osi_handler()`, DMI callbacks that disable Vista/Win7/Win8 strings or enable Linux, `early_acpi_osi_init()`, `acpi_osi_init()`, and `acpi_osi_is_win8()`.

Early flow applies DMI quirks and Apple Darwin setup. Command-line parsing handles empty strings, `!`, `!*`, `!!`, explicit removals, Linux/Darwin special cases, and arbitrary added strings. Later initialization installs the handler and applies queued changes to ACPICA with interface install/remove/update calls.

State is static policy config and an initdata array of up to 16 strings, later materialized in ACPICA's active interface list. Dependencies include ACPICA global OSI controls, DMI matching, Apple x86 platform detection, setup parameter parsing, and OSL initialization. Risks include compatibility regressions for firmware quirks, limited entry/string capacity, subtle `acpi_osi=` semantics, and in this source snapshot a duplicate `static struct acpi_osi_config osi_config;` declaration that should be checked against the intended build baseline. Test signals include command-line permutations, DMI matches, Apple Darwin behavior, Linux/Darwin override precedence, handler logging, and `acpi_osi_is_win8()`.
