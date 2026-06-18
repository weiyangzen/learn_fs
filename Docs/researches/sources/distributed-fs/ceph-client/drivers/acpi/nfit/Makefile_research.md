# sources/distributed-fs/ceph-client/drivers/acpi/nfit/Makefile

Purpose: this Makefile defines how the ACPI NFIT driver is built from its implementation objects.

Important APIs, types, and functions: the build target is `obj-$(CONFIG_ACPI_NFIT) := nfit.o`. The composite object always includes `core.o` and `intel.o`, and conditionally includes `mce.o` when `CONFIG_X86_MCE` is enabled.

Control flow: there is no runtime flow. Kbuild assembles `nfit.o` from the listed objects when `CONFIG_ACPI_NFIT` is enabled as built-in or module.

State and persistence: build composition is determined by kernel configuration. No runtime state is defined here.

Dependencies and integration: integrates NFIT core and Intel-specific support with optional x86 machine-check handling. It relies on the Kconfig option declared in the adjacent `Kconfig`.

Risks: object ordering is simple but meaningful for link inclusion. Conditional MCE support means x86 error-handling features are absent when `CONFIG_X86_MCE` is off, which tests must account for.

Test signals: verify built-in and module builds, `CONFIG_X86_MCE` on/off object composition, and that the resulting module name remains `nfit`.
