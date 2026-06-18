## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_nrtr_regs.h

Purpose: auto-generated TPC7 north-router (`IF_NRTR`) map. It defines 102 `mmTPC7_NRTR_*` offsets from `0xFC0100` to `0xFC0604`, replacing the fuller `TPC_RTR` pattern used by TPC3-TPC6.

Important API surface: HBW/LBW max-credit registers, debug arbiters and maxima, split coefficients/configuration and read/write saturation/token/timeout controls, HBW 64-bit range hit/mask/base tables, LBW 16-entry range hit/mask/base tables, regulator command/result registers, and scrambling controls.

Control flow and state: no executable code. Hardware behavior is controlled by credit, split, range, regulator, and scrambling register values. State persists in the router block until reset/reconfiguration.

Dependencies and integration: included by `goya_regs.h`; base is `mmTPC7_NRTR_BASE`, with no `tpc7_rtr_regs.h` in this subset. CFG/CMDQ/QM for TPC7 integrate with this different routing block.

Risks and test signals: treating TPC7 as a normal RTR can miss credit-control differences. Test TPC7 memory routing, credit exhaustion/timeout behavior, range programming, security access, and end-of-topology traffic.
