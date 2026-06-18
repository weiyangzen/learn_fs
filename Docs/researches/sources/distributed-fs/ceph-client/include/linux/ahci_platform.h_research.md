<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/ahci_platform.h

## Purpose
`ahci_platform.h` declares shared helper APIs for AHCI SATA platform drivers, covering clocks, PHYs, resets, regulators, resources, host initialization, shutdown, and suspend/resume.

## Important APIs, types, and functions
Resource helpers include enable/disable PHYs, clocks, regulators, and all resources, plus reset assert/deassert. Discovery/init helpers include `ahci_platform_find_clk()`, `ahci_platform_get_resources()`, and `ahci_platform_init_host()`. Power/lifecycle helpers include shutdown, host suspend/resume, and device suspend/resume. Flags `AHCI_PLATFORM_GET_RESETS` and `AHCI_PLATFORM_RST_TRIGGER` alter resource acquisition/reset behavior.

## Control flow
Platform probe gets resources, enables power/clock/PHY/reset dependencies in order, initializes the AHCI host, and unwinds on failure. PM paths suspend/resume host and resources.

## State and persistence behavior
Persistent state is in `struct ahci_host_priv` and registered ATA/SCSI host objects. The header only defines function contracts.

## Dependencies and integration points
It integrates libahci, platform devices, clocks, PHYs, regulators, resets, ATA port info, and SCSI host templates.

## Risks and test signals
Risks include resource enable/disable ordering bugs, reset polarity mistakes, missing clock names, and PM imbalance. Test signals include platform AHCI probe failure unwinds, suspend/resume, shutdown, regulator/PHY fault injection, and DT/ACPI platform resource variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ahci_platform.h -->
