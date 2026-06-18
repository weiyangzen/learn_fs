# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_regs.h

## Purpose

`tpc0_eml_cfg_regs.h` is the generated MMIO map for the TPC0 EML/debug configuration block at `0x3040000` through `0x3040334`. It names debug control, watchpoint, trace, and instruction insertion registers.

## Important APIs, Types, and Constants

The file exports `mmTPC0_EML_CFG_*` address constants. It starts with debug control/status, eight program-address watch registers and their count/match registers, vector and scalar address watch pairs, AGU address watch pairs, AXI HBW/LBW address watch pairs, scalar data watch registers, 32 AXI HBW write-data watch registers, AXI LBW write-data watch registers, D0 program counter, RTT config/predicate/interval/timestamp registers, and eight debug instruction insertion slots plus an insertion control register.

## Control Flow

This header has no executable logic. A diagnostic path programs watch registers, enables selected match channels, controls debug entry/exit or single-step through the control register, reads status and program counter, and optionally configures trace predicate/timestamp registers.

## State and Persistence Behavior

The source is generated and immutable during runtime. Hardware register contents persist until reset or reconfiguration. Watch counters, debug status, program counter, and trace-related state change as kernels run and debug events occur.

## Dependencies and Integration Points

It is used with `tpc0_eml_cfg_masks.h` and sits alongside TPC CFG/QM/CMDQ registers for Goya TPC0. It is relevant to low-level debugging, silicon validation, kernel tracing, cache reset/invalidation flows, and any tooling that needs TPC0 execution observability.

## Risks

Wrong addresses can program the wrong watch channel or trace control and make debug behavior nondeterministic. The dense sequential watchpoint layout raises off-by-one risk, especially for 0/1 pairs and the 32-entry AXI HBW data array.

## Test Signals

Validation should read back programmed watchpoint addresses/counts, verify debug status changes after enter/exit/single-step, confirm D0 PC sampling, observe trace predicate/timestamp output, and check instruction insertion only through the documented insertion slots and control address.
