# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_masks.h

## Purpose

`tpc0_eml_cfg_masks.h` defines the generated bitfields for the TPC0 EML/debug configuration block. The fields describe core debug entry/exit, cache invalidation, breakpoints/watchpoints, trace predicates, timestamp tracing, and debug instruction insertion.

## Important APIs, Types, and Constants

The API is `_SHIFT` and `_MASK` macros. `DBG_CNT` controls debug enter, debug enable, core reset, dcache/icache invalidation, debug exit, single-step, and debug software breakpoint enable. `DBG_STS` exposes debug mode, core ready, during-kernel, cache/QM/WQ/MSS idle, and debug cause. Address/data watch families include program address (`PADD`), vector/scalar pointer address (`VPADD`, `SPADD`), AGU address, AXI HBW/LBW address, scalar data, AXI HBW write data, and AXI LBW write data, each with count, match, enable, and read/write selector fields. RTT fields control tracing predicates, interval generation, timestamp generation, and compression. `DBG_INST_INSERT` and `DBG_INST_INSERT_CTL` define injected instruction and insert trigger fields.

## Control Flow

There are no functions. Debug tooling or driver diagnostics writes enable/match registers, asks the core to enter or leave debug, optionally invalidates caches, and reads status/counters to detect breakpoint or trace events.

## State and Persistence Behavior

The macros are static. The underlying registers configure persistent debug hardware state and counters; status bits and watch counts change as TPC0 executes kernels or debug sequences.

## Dependencies and Integration Points

This header pairs with `tpc0_eml_cfg_regs.h` and complements the general TPC CFG register maps. It integrates with TPC kernel execution, cache control, debug stop/single-step handling, RTT trace collection, and low-level silicon bring-up flows.

## Risks

Bad masks can leave TPC0 held in debug/reset, invalidate the wrong cache path, miss or spuriously trigger watchpoints, or generate malformed trace predicates. Address-width differences across PADD, VPADD, SPADD, AGU, and AXI fields are a common source of truncation bugs.

## Test Signals

Signals include debug enter/exit status, single-step progress, cache-idle status after invalidation, watchpoint counts and match registers updating at expected events, RTT interval/timestamp output, and instruction insertion taking effect only when the insert control bit is asserted.
