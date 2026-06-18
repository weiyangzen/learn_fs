# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme1_rtr_masks.h

Purpose: auto-generated bitfield definitions for MME router 1, an `MME_RTR` block. It describes HBW/LBW arbitration, credit, split, range, regulator, and scrambling fields for traffic entering or leaving the first MME router.

Important APIs/types/functions: no functions or types. The `MME1_RTR_*_SHIFT` and `MME1_RTR_*_MASK` macros cover HBW read-request, read-response, write-request, and write-response arbitration across east/west/north/south/local directions; HBW per-direction max credits and request/response max credits; LBW read/write request/response arbitration and credits including SRAM master/slave credits; debug arbitration and max-credit fields; split coefficients/config/rate-limit token/timeout fields; HBW and LBW range hit/mask/base fields; regulator enables/results; and scrambling controls.

Control flow: no executable flow. Driver initialization can use these masks with `mme1_rtr_regs.h` to configure MME mesh routing, credit budgets, range mapping, and optional regulator/scrambling behavior. Diagnostic paths can decode arbiter/range/regulator status.

State and persistence: all described fields are hardware register fields. Arbitration weights, credits, split configuration, range tables, and regulator/scrambling settings persist until reset or rewrite. Status/result fields reflect live or latched hardware diagnostics.

Dependencies and integration: included through `goya_regs.h` and paired with `mme1_rtr_regs.h`. `goya_security.c` protects `mmMME1_RTR_BASE`, and `goya_coresight.c` references MME1 router funnel/debug bases from `goya_blocks.h`. The layout is similar to DMA and TPC router mask headers, supporting common routing concepts.

Risks: MME router masks control performance, ordering, and address routing for accelerator traffic. Bad credit/arbitration masks can starve a direction or deadlock traffic; bad range masks can route requests incorrectly; regulator/scrambling mistakes can affect security or data integrity. The generated typo `WPLIT_WR_TST_TOLEN` must be preserved when referenced.

Test signals: MME workload throughput and correctness, router credit/range readback, error injection or range-hit diagnostics, reset/reprogramming paths, protected-register access checks for `mmMME1_RTR_BASE`, and performance tests under concurrent MME/DMA/TPC traffic.
