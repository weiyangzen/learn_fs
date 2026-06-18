# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme4_rtr_regs.h

## Purpose

`mme4_rtr_regs.h` maps the Goya `MME4_RTR` fabric-router register block. It is generated from the `MME_RTR` prototype and provides stable preprocessor names for MME4 router MMIO offsets used by kernel driver initialization, diagnostics, and range-control paths.

## Important APIs, types, and data

There are no C APIs beyond `#define` constants. The `mmMME4_RTR_*` namespace covers HBW read/write request and response arbitration, HBW credit limits, LBW arbitration and SRAM credits, debug arbiters, split coefficients/configuration, split read/write saturation/reset-token/timeout fields, HBW and LBW range-hit/mask/base arrays, `RGLTR` access/result registers, and scrambler enable/non-linear scrambler controls.

The MME4 register window starts with `mmMME4_RTR_HBW_RD_RQ_E_ARB` at `0x100100` and reaches `mmMME4_RTR_NON_LIN_SCRAMB` at `0x100604`. It is layout-identical to MME2, MME3, MME5, and MME6 router headers except for base address.

## Control flow

The header itself is declarative. Driver code consumes these constants when programming router policy or reading hardware state. Typical control flow is: reset or quiesce the relevant path, write arbitration/credit/range/scrambler registers, enable traffic, then read status/range-hit/debug registers when diagnosing faults.

## State and persistence behavior

Only hardware state changes when these constants are used in MMIO writes. The register contents live in the device and are not persisted by this header. Range masks and bases may remain effective across command submissions, while status and hit registers reflect current or latched hardware observations.

## Dependencies and integration points

This generated file is included by Goya register umbrella headers and low-level device code. It integrates with common HabanaLabs MMIO helpers, Goya reset/security code, and fabric observability through coresight-related blocks. Its main contract is that relative offsets match the `MME_RTR` prototype used by the other router instances.

## Risks and edge cases

A wrong MME4 base or stride calculation can write into a different block. Since this file has no masks, consumers must pair it with the correct field definitions or full-register values from hardware documentation. HBW range programming requires careful low/high pairing. Generated spelling and naming must be treated as ABI for in-tree code even if awkward.

## Test signals

Builds should catch missing macro names. Runtime signals include clean Goya initialization, no MME4 router-related unexpected fault logs, correct register dump ordering from `0x100100` through `0x100604`, and consistent behavior when the same router configuration is applied to MME2-MME6 instances.
