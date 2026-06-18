# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v3-prio.h

## Purpose
`arm-gic-v3-prio.h` defines priority mask values for GICv3 IRQs and pseudo-NMIs as seen through PMR/RPR, including translation validation for the non-secure priority view.

## Important APIs, types, and functions
It defines `GICV3_PRIO_UNMASKED`, `GICV3_PRIO_IRQ`, `GICV3_PRIO_NMI`, `GICV3_PRIO_PSR_I_SET`, conversion macros, and static assertions validating ordering and non-secure round trips.

## Control flow
Architecture IRQ masking code writes these values to PMR, optionally using `GICV3_PRIO_PSR_I_SET` when sections must rely on `PSR.I` rather than priority masking.

## State and persistence
No runtime state is declared.

## Dependencies and integration points
It is shared by GICv3 driver and arm64 entry/interrupt masking code, including pseudo-NMI support.

## Risks and test signals
Risks include invalid values under the NS priority transform and breaking pseudo-NMI ordering. Tests should cover compile-time assertions, IRQ/NMI masking behavior, and arm64 paths that temporarily force `PSR.I`.
