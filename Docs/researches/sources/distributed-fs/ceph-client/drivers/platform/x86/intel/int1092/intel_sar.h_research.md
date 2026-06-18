<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h

## Purpose
Defines constants and data structures for the Intel INT1092 SAR driver.

## Important APIs And Types
Constants include DSM command IDs, driver name `intc_sar`, maximum device modes and regulatory entries, SAR DSM UUID, ACPI notify event, sysfs data name, and expected tuple size. Structures model one device-mode tuple, one regulatory configuration, userspace-supported info, and the full `wwan_sar_context`.

## Control Flow And State
The header owns no code. It defines the persistent in-memory shape used by `intel_sar.c` for parsed BIOS tables and exposed current SAR data.

## Dependencies And Integration Points
Depends on platform device and ACPI types included by the C file. The field names reflect the sysfs data contract and userspace modem SAR expectations.

## Risks And Test Signals
Risks are fixed maximums not matching future firmware and unused/stale fields such as `supported_data`. Test by compiling with `intel_sar.c` and validating sysfs output tuple order against userspace consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h -->
