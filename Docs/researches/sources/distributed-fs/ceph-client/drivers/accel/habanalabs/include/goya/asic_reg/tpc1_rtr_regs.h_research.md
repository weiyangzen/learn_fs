# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_rtr_regs.h

## Purpose

`tpc1_rtr_regs.h` is the generated address map for the Goya TPC1 router block, from `0xE40100` through `0xE40604`. It exposes HBW/LBW arbitration, split/rate, range decoding, regulator, and scrambling controls.

## Important APIs, Types, and Constants

The `mmTPC1_RTR_*` constants include HBW read-request, read-response, write-request, and write-response arbitration registers for east/west/north/south/local routes, plus HBW max-credit controls. LBW has equivalent route arbitration and max-credit groups. Debug arbitration and max-credit groups follow, then ten split coefficients, split config, read/write saturation, token and timeout controls, 8 HBW range mask/base low/high entries with hit indicator, 16 LBW range mask/base entries with hit indicator, regulator control/result registers, and scrambler enable/non-linear scrambler registers.

## Control Flow

No executable control flow is present. Router setup code writes arbitration weights, credits, range tables, rate controls, and scrambling options; diagnostics read hit/debug/result registers during traffic tests.

## State and Persistence Behavior

The registers retain routing configuration until reprogrammed or reset. Hit/result/debug fields expose live or latched router observations tied to memory traffic.

## Dependencies and Integration Points

This map integrates with Goya TPC1 memory fabric access, HBW/LBW routing, mesh topology, performance tuning, and silicon validation. It complements TPC1 CFG/QM/CMDQ maps by defining the memory path around the core.

## Risks

Incorrect arbitration or credits can starve directions or hang traffic. Range table mistakes can route transactions to the wrong memory path. Split and scrambling controls can affect ordering, latency, and data-path assumptions.

## Test Signals

Expected HBW/LBW range-hit bits, sustained bidirectional traffic without stalls, arbitration fairness under mixed route load, timeout behavior when rate limiters are enabled, regulator result readback, and correct operation with scrambling settings are key signals.
