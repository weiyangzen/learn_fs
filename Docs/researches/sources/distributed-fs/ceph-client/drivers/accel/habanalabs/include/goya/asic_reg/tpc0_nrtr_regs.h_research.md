# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_regs.h

## Purpose

`tpc0_nrtr_regs.h` is the generated address map for the Goya TPC0 north router block, covering `0xE00100` through `0xE00604`. It exposes credit, debug arbitration, split/range, regulator, and scrambling registers.

## Important APIs, Types, and Constants

The file exports `mmTPC0_NRTR_*` MMIO addresses. Key groups are HBW/LBW max credit registers, debug arbitration registers for east/west/north/south/local routes and their max-credit controls, ten split coefficient registers, split config and read/write rate limit registers, 8-entry HBW range hit/mask/base tables using low/high components, 16-entry LBW range hit/mask/base tables, regulator control and result registers, and scrambler enable/non-linear scrambler registers.

## Control Flow

There are no functions. Driver or bring-up code writes addresses from this map to configure router topology and address decoding, then reads hit/result/debug registers while validating traffic flow.

## State and Persistence Behavior

Register values are hardware state. Credit/range/split/scrambler configuration remains active until reset or update. Range hit and regulator result registers expose state derived from recent or active routing operations.

## Dependencies and Integration Points

This map is consumed with `tpc0_nrtr_masks.h` and integrates with the Goya TPC0 memory path, mesh/router programming, address range partitioning, and performance or debug controls. It is conceptually related to the later TPC RTR maps, which add fuller HBW/LBW arbitration families.

## Risks

Address-map mistakes can cause traffic misrouting or fabric stalls. Dense range-table addresses are especially risky because an index error may still program a valid neighboring range.

## Test Signals

Validation includes readback of configured credit/range tables, expected range hit indicators for HBW and LBW accesses, successful high-bandwidth and low-bandwidth traffic through TPC0, regulator result changes, and no unexpected timeout/starvation when split rate controls are active.
