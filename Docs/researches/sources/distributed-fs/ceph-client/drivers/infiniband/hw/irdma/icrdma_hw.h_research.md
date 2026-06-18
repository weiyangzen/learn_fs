# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_hw.h

## Purpose
`icrdma_hw.h` defines Gen2 IRDMA register offsets, doorbell offsets, CQP field masks/shifts, and capability constants used by `icrdma_hw.c`.

## Important APIs, types, and functions
The header exports `icrdma_init_hw`. Important definitions include PF/VF queue registers, `GLINT_DYN_CTL`, `GLINT_CEQCTL`, `VSIQF_PE_CTL1`, HMC invalidation registers, `GLINT_RATE`, CQP status and field masks, and `enum icrdma_device_caps_const`.

## Control flow, state, and persistence
There is no runtime control flow; it provides compile-time constants that become the runtime `hw_regs`, `hw_masks`, `hw_shifts`, and capability attributes after initialization.

## Dependencies and integration points
It includes `irdma.h`, so its masks are tied to the common register/mask/shift enum ordering. It is used by the Gen2 hardware adapter and indirectly by common control initialization.

## Risks and test signals
Risks are duplicated or stale definitions, wrong CQP bit positions, and mismatched register offsets. Test signals include CQP command encode/decode validation, interrupt register smoke tests, and capability checks for ORD/IRD and push-page limits.
