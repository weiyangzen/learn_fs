# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.h

Purpose: small IPMI DMI helper header that exposes DMI-derived slave-address lookup when DMI decoding is enabled.

Important APIs, types, and functions: includes `ipmi_si.h` for `enum si_type` and conditionally declares `ipmi_dmi_get_slave_addr()`.

Control flow: no runtime flow. Compile-time `CONFIG_IPMI_DMI_DECODE` decides whether consumers may call the lookup symbol.

State and persistence: no state in the header; state lives in `ipmi_dmi.c`'s decoded DMI list.

Dependencies and integration: used by IPMI SI/platform code needing to reconcile ACPI-described interfaces with SMBIOS slave addresses. It depends on `ipmi_si.h` declarations.

Risks and test signals: conditional declaration must stay aligned with the exported implementation and config symbol. Tests should include builds with and without `CONFIG_IPMI_DMI_DECODE`, plus users including the header through different IPMI build paths.
