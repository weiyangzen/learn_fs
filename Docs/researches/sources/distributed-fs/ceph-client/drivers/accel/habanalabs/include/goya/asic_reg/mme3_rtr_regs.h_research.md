# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme3_rtr_regs.h

## Purpose

`mme3_rtr_regs.h` is the generated register-offset map for the Goya `MME3_RTR` block. It represents the same `MME_RTR` prototype as `MME2_RTR`, but relocated to the MME3 router address window. The macros let driver code name MME3 fabric-router registers without embedding numeric MMIO constants.

## Important APIs, types, and data

This file exports only `#define` constants in the `mmMME3_RTR_*` namespace. The register families are HBW arbitration and credit control, LBW arbitration and SRAM credit control, debug arbitration maxima, split coefficients and split read/write timeout controls, HBW and LBW range-hit/mask/base programming, register-lane access/result registers, and scrambler controls.

The first listed register is `mmMME3_RTR_HBW_RD_RQ_E_ARB` at `0xC0100`; the final register is `mmMME3_RTR_NON_LIN_SCRAMB` at `0xC0604`. Relative offsets match `mme2_rtr_regs.h`, so this file is a base-address specialization rather than a distinct programming model.

## Control flow

No control flow exists inside the header. Consumers use these constants in MMIO access sequences for router initialization, range setup, fabric debugging, and reset recovery. When software needs to apply one policy across several MME routers, it can use the repeated layout and substitute the MME3 base window.

## State and persistence behavior

The header has no mutable host state. Hardware writes to MME3 router registers persist in the device until reset or replacement writes. Range-base/mask registers determine what addresses the MME3 router recognizes, arbitration and credit registers affect live traffic scheduling, and scrambler controls affect address/data transformation behavior on the path.

## Dependencies and integration points

The file depends only on its include guard and the generated-register inclusion convention. It integrates with Goya initialization, security/range programming, coresight/monitoring code that maps MME router trace/funnel blocks, and common register access macros. The sibling router files are direct peers and should remain layout-compatible.

## Risks and edge cases

Because the file is auto-generated, hand edits are risky and would diverge from the authoritative register database. Code that computes offsets across router instances must account for the `0x40000` stride between these MME router blocks. HBW uses split high/low mask and base fields; LBW uses a single 32-bit mask/base per slot. Misprogramming range slots can silently redirect, expose, or block fabric traffic.

## Test signals

Compile coverage should prove that all macros referenced by Goya code exist. Runtime validation is successful probe/reset and MME workload execution with no unexpected MME3 router range-hit or fabric errors. Low-level register dump tools should show MME3 values at the `0xC0xxx` window while preserving the same relative layout as other MME router instances.
