# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_core_regs.h

## Purpose

`dma4_core_regs.h` is the generated register map for `DMA4_CORE`, a Gaudi DMA core block. It provides 67 `mmDMA4_CORE_*` offsets from `0x580000` to `0x580238`; `gaudi_blocks.h` lists `mmDMA4_CORE_BASE` as `0x7FFC580000ull`. DMA4 is managed as an HBM DMA engine.

## Important APIs, Types, And Register Groups

The file contains macro definitions only. Functional groups are configuration and halt, LBW outstanding workaround control, source/destination base registers, source/destination multidimensional sizes and strides, commit, write completion data/address/user registers, tensor-engine rows, protection and secure/non-secure properties, read/write outstanding and cache controls, rate limits, error cause/config/message registers, status registers, read debug memory controls, and debug counters for HBW/LBW AXI plus descriptors.

## Control Flow And State

There is no local control flow. DMA4 is programmed by common DMA-core routines through `4 * DMA_CORE_OFFSET`, and by direct HBM stall writes to `mmDMA4_CORE_CFG_1`. Initialization enables the core and configures error-message routing and secure MMU bypass. Transfer code writes source/destination/size and commits, then polls `STS0` and reads `ERR_CAUSE`.

State is entirely in hardware: active transfer descriptors, completion writeback registers, outstanding/inflight counters, rate limit knobs, error state, and security/ASID properties. Reset restore rewrites completion target and `WR_AWUSER_31_11` for DMA4 as an HBM channel. MMU preparation updates `mmDMA4_CORE_NON_SECURE_PROPS`.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h`. It depends on the shared DMA core register shape used by `DMA_CORE_OFFSET` in `gaudiP.h` and field definitions from sibling headers. Integration points include HBM DMA init/stall/disable flows, debugfs DMA read and transfer helper paths, engine idle reporting, reset restore, and MMU ASID setup.

## Risks And Test Signals

Critical risks are memory corruption from source/destination/commit offset errors, lost or misdirected write completions, and security faults from non-secure property drift. A wrong `CFG_1` halt offset can leave DMA4 running during reset. Test signals include DMA4 HBM traffic completing, no transfer timeouts, idle status after stop, zero error cause after operations, correct write-completion restoration after reset, and successful MMU-context workloads.
