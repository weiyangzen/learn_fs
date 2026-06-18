<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig

## Purpose
Defines the Intel `INTC1092` Specific Absorption Rate driver option.

## Important Symbol
`INTEL_SAR_INT1092` is a tristate depending on ACPI. Its help describes exporting BIOS-provided modem SAR configuration to userspace so a front-end can configure an Intel M.2 modem over MBIM or similar channels.

## Control Flow And State
Build-time only. When enabled, the Makefile builds `intel_sar.o` and the platform driver can bind ACPI HID `INTC1092`.

## Dependencies, Risks, And Test Signals
Risks are exposing an option without the expected userspace modem integration and ACPI DSM ABI. Test module build and ACPI binding on systems with `INTC1092`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig -->
