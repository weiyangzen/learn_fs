# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme6_rtr_regs.h

## Purpose

`mme6_rtr_regs.h` is the generated register-offset map for the Goya `MME6_RTR` block. It supplies symbolic MMIO offsets for the final MME router instance in this header group and shares the `MME_RTR` prototype layout with MME2-MME5.

## Important APIs, types, and data

The file defines only `mmMME6_RTR_*` macros. The key register groups are HBW arbitration and credit controls, LBW arbitration and SRAM credit controls, debug arbiters and maxima, split coefficients and split read/write control, HBW and LBW range hit/mask/base arrays, `RGLTR` read/write-result registers, and scrambler enable/non-linear scrambler registers.

The address range is `0x180100` to `0x180604`. HBW range entries are eight-slot low/high pairs; LBW range entries are sixteen single-register mask/base slots.

## Control flow

The header is declarative, with no branches or calls. Device code uses these constants for MMIO reads/writes during router setup, reset, security/range configuration, and hardware debug. Any multi-router sequence should treat this file as the `0x180000` base specialization of the common router layout.

## State and persistence behavior

State is in hardware only. Writes to arbitration, split, range, and scrambler registers persist in the MME6 router until reset or overwrite. Reads of range-hit and result registers observe the device state; no host persistence is created by the header.

## Dependencies and integration points

It depends on the generated register database and include guard. Integration points are Goya low-level register programming, fabric diagnostics, security/range policies, and common HabanaLabs MMIO access helpers. The sibling router headers form a consistency set and should be regenerated together.

## Risks and edge cases

The final router instance has the largest address base in this group, so integer type assumptions in consumers should preserve full offsets. Manual correction of generated names can break include users. Misprogrammed range registers may only show up as later fabric faults or inaccessible address windows, making runtime validation important.

## Test signals

Compile all Goya/HabanaLabs code, run Goya probe/reset, execute MME workloads, and inspect any router range-hit or scrambler-related debug output. Register dumps should show the same relative layout as MME2-MME5 at the `0x180xxx` address window.
