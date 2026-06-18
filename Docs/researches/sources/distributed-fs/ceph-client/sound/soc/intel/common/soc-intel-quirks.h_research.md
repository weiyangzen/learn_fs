# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h

## Purpose
Provides a shared inline Bay Trail CR platform-detection helper for Intel SST and SOF drivers, allowing both stacks to handle legacy Bay Trail interrupt-resource quirks consistently.

## Important APIs, Types, And Functions
`soc_intel_is_byt_cr(struct platform_device *pdev)` is the only exported header API. When `CONFIG_IOSF_MBI` is reachable, it checks SoC family, a DMI force table for Lenovo Yoga Tablet 2 systems, IOSF PUNIT `BIOS_CONFIG` PMIC bits, and a fallback IRQ-resource layout check. Without IOSF MBI support it compiles to `false`.

## Control Flow, State, And Persistence
The helper is inline and stateless. It returns early on non-Bay Trail systems, forced DMI matches, successful PMIC-bit detection, and missing IRQ index 5. It logs detection or fallback decisions through the platform device.

## Dependencies And Integration Points
Depends on `linux/platform_data/x86/soc.h`, DMI, IOSF MBI, and platform IRQ resources. Integration is by including the header from SST/SOF platform drivers that need to know whether IPC IRQ index 0 should be used as on Bay Trail CR.

## Risks And Test Signals
Risks are false positives from the IRQ-resource fallback, unavailable IOSF MBI on systems that need precise detection, and stale DMI exceptions. Test signals include Bay Trail CR and non-CR boot logs, IPC IRQ selection, and compile coverage with and without `CONFIG_IOSF_MBI`.
