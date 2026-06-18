<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h

## Purpose

`clk.h` is the private Ux500 clock helper interface shared by PRCC, PRCMU, sysctrl, ABX500, and U8500 clock-definition code.

## Important APIs, Types, And Functions

It declares PRCC pclk/kclk registration, PRCMU scalable/gate/rate/OPP/clkout registration, and sysctrl gate/fixed-rate/parent-selector registration. The prototypes establish which helpers return legacy `struct clk *` versus `struct clk_hw *`.

## Control Flow

There is no executable flow. Compile-time inclusion lets definition files construct the clock tree without exposing implementation structs.

## State And Persistence Behavior

The header owns no state. It defines the function boundaries through which U8500 setup stores clocks in provider arrays and ABX500 setup exposes PMIC clocks.

## Dependencies And Integration Points

It includes Linux device and integer types and forward-declares `struct clk` and `struct clk_hw`. It is integrated only inside `drivers/clk/ux500`.

## Risks And Test Signals

The main risk is ABI drift inside the driver directory: changing return types or argument order breaks multiple files. Build tests with all Ux500 objects catch this; runtime tests should verify both `struct clk *` and `struct clk_hw *` providers are populated correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h -->
