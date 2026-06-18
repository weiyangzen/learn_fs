# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_regs.h

Purpose: auto-generated register-address map for MME router 1, the first MME mesh router block using the `MME_RTR` prototype.

Important APIs/types/functions: no functions or structs. The `mmMME1_RTR_*` macros map HBW read-request/read-response/write-request/write-response arbitration and credit registers, LBW arbitration and credits, debug arbitration and max credits, split coefficients and config/token/timeout controls, HBW and LBW range hit/mask/base arrays, regulator config/result registers, and scrambling controls.

Control flow: declarative. Driver initialization and tuning code can program routing and credit tables, split behavior, range maps, and regulator/scrambling settings using these offsets and `mme1_rtr_masks.h`. Diagnostic code can read arbitration, range-hit, and result registers.

State and persistence: router state is in hardware. Programmed arbitration weights, credits, range tables, and split config persist until reset or rewrite; status/result registers expose current or latched hardware behavior. `goya_blocks.h` defines `mmMME1_RTR_BASE` and max offset `0x608`.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` protects the MME1 router block, and `goya_coresight.c` references related MME1 router funnel/CoreSight bases. The register layout parallels other router headers such as `dma_nrtr_regs.h`.

Risks: MME router misprogramming can affect accelerator traffic ordering, throughput, and address routing. Incorrect offsets or array bounds can overwrite the wrong router controls. Since this is one MME router among several, using MME1 addresses for other MME instances would target the wrong hardware.

Test signals: MME workload execution, router configuration readbacks, traffic/performance counters under load, range-hit diagnostics, regulator/scrambling validation where supported, reset sequencing, and protected-block access checks for the MME1 router window.
