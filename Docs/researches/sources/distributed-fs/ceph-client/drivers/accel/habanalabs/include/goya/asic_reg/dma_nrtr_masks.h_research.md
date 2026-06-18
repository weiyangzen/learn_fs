# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_nrtr_masks.h

Purpose: auto-generated bitfield definitions for the DMA north router (`DMA_NRTR`), an `IF_NRTR`-style routing block that controls DMA HBW/LBW arbitration, split behavior, address-range mapping, regulators, and scrambling.

Important APIs/types/functions: exposes `DMA_NRTR_*_SHIFT` and `DMA_NRTR_*_MASK` macros. Key groups include HBW/LBW max credits for write request/write response/read request/read response, debug arbitration fields for east/west/north/south/local directions, per-direction max debug credits, split coefficients and split config flags (`FORCE_WAK_ORDER`, `FORCE_STRONG_ORDER`, `DEFAULT_MESH`, read/write rate-limit enables, `B2B_OPT`), split token/timeout fields, HBW/LBW range hit/mask/base fields, regulator enable/result fields, and scrambling enable fields.

Control flow: no code executes here. Driver code writes the paired addresses in `dma_nrtr_regs.h` using these masks to set credit budgets, routing coefficients, range tables, and optional rate limiting. Error handling can read result and diagnostic registers with the same masks.

State and persistence: all state is in router registers. Credits and routing/range configuration persist until rewritten or reset. Regulator and scrambling settings affect subsequent transactions rather than host-side state.

Dependencies and integration: included via `goya_regs.h` and used with `dma_nrtr_regs.h`. `goya_security.c` explicitly protects `mmDMA_NRTR_BASE`, and `goya_blocks.h` maps the block at `0x7FFC1C0000`.

Risks: router credit and range fields shape global DMA traffic. Incorrect masks can starve directions, reorder traffic unexpectedly, or map transactions to an unintended mesh path. The generated typo `WPLIT_WR_TST_TOLEN` must be matched exactly by any code using that register family.

Test signals: boot-time router programming, DMA traffic across all mesh directions, read/write rate-limit behavior, forced error/range-hit tests, register readback of split and range tables, and security tests confirming the router block is protected from untrusted access.
