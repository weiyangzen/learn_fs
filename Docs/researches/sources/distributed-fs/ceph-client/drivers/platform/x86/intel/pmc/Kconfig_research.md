<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig

## Purpose
Defines Intel PMC core and SSRAM telemetry support.

## Important Symbols
`INTEL_PMC_CORE` is a tristate depending on PCI, ACPI, and Intel PMT telemetry; it selects `INTEL_PMC_SSRAM_TELEMETRY`. `INTEL_PMC_SSRAM_TELEMETRY` is hidden and builds the SSRAM telemetry helper.

## Control Flow And State
Build selection enables the PMC core and a platform driver for accessing Intel Power Management Controller registers, S0ix residency, IP power-gating, LTR, low-power-mode, and platform-specific quirks.

## Dependencies And Integration Points
Depends on PCI, ACPI, PMT telemetry, and platform-specific register maps in the sibling Makefile.

## Risks And Test Signals
Risks are missing telemetry dependency or unintentional disabling of PMC diagnostics. Test with supported Intel platforms and verify debugfs/telemetry features are present when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig -->
