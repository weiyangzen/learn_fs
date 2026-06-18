# sources/distributed-fs/ceph-client/drivers/acpi/acpi_ffh.c

## Purpose
`acpi_ffh.c` installs an ACPI Fixed Function Hardware address-space handler and delegates all architecture-specific setup and accesses to weak arch-overridable hooks.

## Important APIs, Types, And Functions
The file defines weak defaults `acpi_ffh_address_space_arch_setup()` and `acpi_ffh_address_space_arch_handler()`, both returning `-EOPNOTSUPP`. It wraps them with ACPICA-compatible `acpi_ffh_address_space_setup()` and `acpi_ffh_address_space_handler()`, and exposes `acpi_init_ffh()` to install the handler for `ACPI_ADR_SPACE_FIXED_HARDWARE`.

## Control Flow
During ACPI initialization, `acpi_init_ffh()` calls `acpi_install_address_space_handler()` on `ACPI_ROOT_OBJECT`. Region setup calls the arch setup hook with handler context and region context. AML accesses call the arch handler to populate or consume the ACPI integer value.

## State And Persistence
The only file-local state is `ffh_ctx`, passed as handler context. Any meaningful per-region state is supplied by architecture implementations through `region_context`.

## Dependencies And Integration Points
It depends on ACPICA address-space handling and architecture code that overrides the weak functions, commonly for platform-specific FFH operation regions or C-state support.

## Risks
Without arch overrides, FFH accesses return unsupported. Handler install failure is logged only as an alert; callers must tolerate missing FFH support. The generic handler ignores function, address, and bit-width parameters and relies entirely on arch code.

## Test Signals
Build tests should cover configurations with and without arch overrides. Runtime validation should verify handler installation, region setup, successful arch-backed reads/writes, and graceful unsupported behavior.
