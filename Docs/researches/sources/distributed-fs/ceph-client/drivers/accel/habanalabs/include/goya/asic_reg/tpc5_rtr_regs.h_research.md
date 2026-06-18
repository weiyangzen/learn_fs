## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_rtr_regs.h

Purpose: auto-generated TPC5 router map. It defines 150 `mmTPC5_RTR_*` offsets from `0xF40100` to `0xF40604`.

Important API surface: HBW/LBW arbitration for read/write request/response channels in five directions, arbiter maximums, debug arbiters, split coefficients/configuration and timeout/token controls, HBW/LBW range hit/mask/base registers, regulator command/result registers, and scrambling controls.

Control flow and state: no functions or branches. External initialization writes routing and arbitration parameters; the hardware router then applies them to TPC5 traffic. State is volatile device register state.

Dependencies and integration: included by `goya_regs.h`; base metadata in `goya_blocks.h`; surrounding driver code uses the TPC router blocks for security configuration and coresight routing.

Risks and test signals: bad route tables can isolate or misdirect TPC5 memory paths. Test with per-TPC memory traffic, arbitration throughput checks, range-hit diagnostics, protection-bit programming, and hardware spec diffing.
