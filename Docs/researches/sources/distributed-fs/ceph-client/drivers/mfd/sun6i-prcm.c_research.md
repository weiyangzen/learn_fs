# sources/distributed-fs/ceph-client/drivers/mfd/sun6i-prcm.c

## Purpose
`sun6i-prcm.c` is the Allwinner PRCM MFD parent. It splits one PRCM memory resource into clock, reset, and codec-analog child devices based on SoC compatible.

## Important APIs, Types, and Functions
`struct prcm_data` stores the selected child list. Static `mfd_cell` arrays describe sun6i-a31 and sun8i-a23 PRCM subdevices and their relative memory resources. `sun6i_prcm_probe()` selects match data, gets the parent memory resource, and calls `mfd_add_devices()`.

## Control Flow
The built-in platform driver matches the PRCM node, picks the SoC-specific `prcm_data`, verifies a memory resource exists, and registers all child cells with the parent resource as the base for relative offsets.

## State and Persistence
The file has no allocated runtime state. Hardware state is managed by child clock/reset/codec drivers.

## Dependencies and Integration Points
It depends on MFD core, OF matching, and child drivers for Allwinner AR100/APB0 clocks, gate clocks, reset control, IR clock, and codec analog blocks.

## Risks and Edge Cases
Relative child resources assume the parent resource covers all offsets. Missing parent memory resource returns `-ENOENT`. The driver uses `builtin_platform_driver()`, making it part of early platform setup rather than a loadable module path.

## Test Signals
Boot on sun6i-a31 and sun8i-a23 DTs, child resource offsets, clock/reset provider registration, codec analog child on sun8i-a23, and failure logging for missing memory resources are useful signals.
