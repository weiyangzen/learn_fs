## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cfg_regs.h

Purpose: auto-generated TPC7 configuration map defining 432 `mmTPC7_CFG_*` offsets from `0xFC6400` through `0xFC6E2C`.

Important API surface: mirrored `KERNEL_*` and `QM_*` descriptor banks with eight tensor descriptors, five TID dimensions, 32 SRF registers, base/config/sync-message controls, plus common TPC registers for TBUF, semaphores, flags, status, CFG/SM base translation, command/execute/stall, icache, MSS, TSB, interrupts, ARUSER/AWUSER, and MBIST.

Control flow and state: no code. Software or firmware writes descriptor/control registers and hardware updates status/interrupt fields. State is in TPC7 hardware registers.

Dependencies and integration: included by `goya_regs.h`; base declared as `mmTPC7_CFG_BASE`; async events cover TPC7 ECC/decoder/kernel errors. TPC7 differs from prior routers by pairing with `TPC7_NRTR`, not `TPC7_RTR`.

Risks and test signals: final TPC lane often exposes off-by-one or topology-specific bugs. Test TPC7 kernel dispatch, descriptor programming, stall/recovery, interrupts, MBIST, security windows, and interaction with TPC7 NRTR routing.
