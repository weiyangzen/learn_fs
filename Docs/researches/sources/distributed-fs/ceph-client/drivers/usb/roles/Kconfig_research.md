<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig

Purpose: declares the generic USB role-switch class and the Intel xHCI role-switch driver configuration. It controls whether role switching is available to dual-role controllers and mux drivers.

Important APIs/types/functions: Kconfig symbols `USB_ROLE_SWITCH` and `USB_ROLES_INTEL_XHCI`; module names `roles.ko` and `intel-xhci-usb-role-switch`.

Control flow and state: no runtime flow; configuration exposes the Intel option only inside `if USB_ROLE_SWITCH` and requires `ACPI && X86`. The persistent effect is build configuration, which determines whether role-switch APIs and modules exist.

Dependencies and integration points: USB role-switch public API, USB controller/mux/connector drivers, ACPI x86 Intel SoCs, and the local Makefile object mappings.

Risks and test signals: risks are platform misconfiguration, module/builtin mismatches with role-switch consumers, and stale module help text. Test with menu visibility, `allmodconfig`, `allyesconfig`, x86 ACPI builds, and module-name checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/Kconfig -->
