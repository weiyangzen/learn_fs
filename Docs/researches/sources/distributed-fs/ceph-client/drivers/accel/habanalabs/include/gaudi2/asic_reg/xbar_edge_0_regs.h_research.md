# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_edge_0_regs.h

## Purpose
`xbar_edge_0_regs.h` defines the generated register address map for Gaudi2 XBAR edge instance 0. It configures low-bandwidth/debug routing windows, HBM/PC bit placement, arbitration, rate limiting, credit state, and data-width conversion behavior.

## Important APIs, Types, And Functions
The macros cover LBW and DBG base/mask pairs for HIF, HMMU, EDMA, HBM, and XBAR targets; internal address routing registers; EMEM/HBM and EMEM/PC bit locations; HIF write response channel location; HBW master arbitration weight; MMU page-cache index maps; MMU read/write low-latency arbitration; HBM user response overrides; read and write rate limiters 0-11; end-to-end credit slave registers; credit debug; upscale/down-conversion controls; and down-conversion LFSR configuration.

## Control Flow
There is no executable code. Driver/security setup writes the address-window and conversion registers to route transactions across the XBAR, then may tune rate limiting, arbitration, and credits. Diagnostic code reads debug and credit registers.

## State, Persistence, And Dependencies
All state is XBAR hardware configuration. It persists until reset or reprogramming and affects fabric routing and memory access behavior. It depends on device address maps, HBM/PCIe layout, MMU configuration, and security policy.

## Integration Points
Cross-references show Gaudi2 security code enumerating XBAR edge ranges and selected conversion registers. The block integrates with memory fabric setup, protected register access, MMU/HIF/HBM routing, rate limiting, and debug flows.

## Risks
Bad base/mask programming can misroute MMIO or memory traffic. Rate limiter and arbitration mistakes can throttle or starve engines. Data-width conversion and LFSR settings can affect protocol correctness. Security exposure is high because XBAR routing defines which masters can reach which targets.

## Test Signals
Tests should cover expected access through each LBW/DBG window, HBM and PCIe traffic routing, MMU page-cache mapping, rate limiter behavior under load, security register-range enforcement, and no regressions in bandwidth or fabric error counters.
