# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-smc.h

## Purpose

This 121-line header defines Atmel SMC/HSMC chip-select timing register layout, configuration structure, and helper APIs for static memory and NAND-like devices.

## Important APIs, Types, and Functions

It exports setup/pulse/cycle/mode/timings offset macros for SMC and HSMC layouts, timing field shifts, mode bitfields for read/write mode, external wait, bus width, TDF, page mode, and NAND timings, `struct atmel_hsmc_reg_layout`, `struct atmel_smc_cs_conf`, init/set/apply/get helper prototypes, and `atmel_hsmc_get_reg_layout()`.

## Control Flow

Driver flow initializes a `atmel_smc_cs_conf`, sets setup/pulse/cycle/timing values with validating helpers, then applies the result to a chip select using a regmap and optional HSMC layout.

## State and Persistence Behavior

Configuration lives in the stack/static struct until applied, then persists in SMC/HSMC hardware registers and controls external bus timing.

## Dependencies and Integration Points

It integrates Atmel memory controller support with device-tree, regmap, NAND, NOR, and other external bus devices.

## Risks and Edge Cases

Timing helpers must reject values outside bitfield capacity. SMC and HSMC register strides differ, so the correct layout function is required. Wrong timings can corrupt external memory transactions.

## Test Signals

Unit tests for timing/set helper bounds, apply/get round trips on mock regmap, device-tree layout tests, and hardware tests for NAND/NOR timing stability.
