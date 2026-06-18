## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_rtr_regs.h

Purpose: auto-generated TPC6 router register map. It defines 150 `mmTPC6_RTR_*` offsets from `0xF80100` through `0xF80604`.

Important API surface: HBW and LBW arbitration registers for read/write requests and responses, arbiter maxima, debug arbiters, split coefficients and read/write split control, HBW and LBW address range hit/mask/base tables, regulator read/write result registers, and scrambling controls.

Control flow and state: declarative register constants only. Runtime hardware routing depends on values written into these registers by initialization, debug, or firmware flows. State is volatile across reset.

Dependencies and integration: included by `goya_regs.h`; paired with `mmTPC6_RTR_BASE`; coresight and security code depend on matching router block locations.

Risks and test signals: route/range mistakes can cause data-path faults for TPC6 traffic and hard-to-diagnose timeout behavior. Test with TPC6 memory routes, HBW/LBW range coverage, arbitration stress, protection-bit programming, and generated spec comparison.
