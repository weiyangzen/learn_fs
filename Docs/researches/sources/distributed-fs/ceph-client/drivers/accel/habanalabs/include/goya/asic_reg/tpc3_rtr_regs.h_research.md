## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_rtr_regs.h

Purpose: auto-generated Goya TPC3 router register map for the `TPC_RTR` block. It defines 150 `mmTPC3_RTR_*` offsets from `0xEC0100` to `0xEC0604`, corresponding to `mmTPC3_RTR_BASE` and `TPC3_RTR_MAX_OFFSET` in `goya_blocks.h`.

Important API surface: high-bandwidth and low-bandwidth arbitration registers for read requests, read responses, write requests, and write responses in east/west/north/south/local directions; arbiter max registers; debug arbiter registers; split coefficients/configuration; read/write saturation, token reset, and timeout controls; HBW and LBW range hit/mask/base tables; regulator access/result registers; scrambling enable and non-linear scrambling controls.

Control flow and state: no functions are present. Hardware control flow is external: initialization or debug code writes arbitration/range/split values, then the TPC router routes memory traffic according to those registers. State persists in the device until reset or reprogramming.

Dependencies and integration: included by `goya_regs.h`; base ranges are also used by coresight funnel/debug metadata and security setup. Router configuration must agree with address decoding, HBW/LBW topology, and TPC enable masks.

Risks and test signals: address or range-table mistakes can misroute traffic, starve ports, or corrupt isolation. Test with TPC memory traffic, HBW/LBW range hit diagnostics, protection-bit access tests, timeout/error interrupt paths, and comparison against generated hardware specs.
