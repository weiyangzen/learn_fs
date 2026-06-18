# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_cfg_regs.h

## Purpose

This generated header defines the Gaudi TPC6 configuration register offsets. It mirrors the TPC4/TPC5 CFG layout for the TPC6 address aperture and gives driver code symbolic `mmTPC6_CFG_*` names for tensor descriptors, kernel launch fields, execution controls, debug/MBIST controls, and the queue-manager-visible TPC configuration image. It contains 602 macros from `mmTPC6_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF86400` through `mmTPC6_CFG_QM_SRF_31` at `0xF86E3C`.

## Important APIs, types, and macros

The public API is the macro list. Important groups are `KERNEL_TENSOR_0..15_*`, `KERNEL_SYNC_OBJECT_*`, `KERNEL_KERNEL_BASE_ADDRESS_*`, TID base/size registers for dimensions 0..4, `KERNEL_CONFIG`, `KERNEL_ID`, `KERNEL_SRF_0..31`, common CFG controls such as `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, interrupt and rate-limit registers, ARUSER/AWUSER controls, LUT base registers, TSB/debug-memory counters, MBIST registers, and the mirrored `QM_TENSOR_0..15_*` and `QM_SRF_0..31` family.

## Control flow and state behavior

There is no code path inside the header. Consumers use these offsets for MMIO. Observed flows include stalling TPC6 with `mmTPC6_CFG_TPC_STALL`, preparing ASID-related `mmTPC6_CFG_ARUSER_LO` and `mmTPC6_CFG_AWUSER_LO`, and building protection-bit masks for the TPC6 CFG register window. The state represented is hardware register state, not software persistence.

## Dependencies and integration points

The header is included by `gaudi_regs.h` and corresponds to `mmTPC6_CFG_BASE` in `gaudi_blocks.h` (`0x7FFCF86000ull`). It integrates with Gaudi reset, MMU, and security code and relies on common bitfield definitions from the equivalent TPC0 registers for shifts/masks.

## Risks and test signals

The file should be treated as generated source of truth. Incorrect offsets affect only TPC6 by name but can break common multi-TPC loops and protection calculations. Tests should include Gaudi build coverage, TPC6 stall/reset scenarios, MMU ASID propagation through CFG user attributes, security protection-window validation, and generated-layout comparisons across TPC4/TPC5/TPC6.
