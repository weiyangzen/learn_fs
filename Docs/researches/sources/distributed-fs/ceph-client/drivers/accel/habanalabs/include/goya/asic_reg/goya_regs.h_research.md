# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_regs.h

Purpose: umbrella register include for the Goya ASIC. It aggregates block-base definitions, per-block register-address headers, selected mask headers, and a small set of chip-level register aliases into one include for Goya driver code.

Important APIs/types/functions: no functions or structs. Its public surface is all included `mm*` register macros and bitfield masks, plus local aliases for PCIe DBI device/MSI-X doorbell registers, sync-manager SOB and monitor ranges, and `mmGIC_DISTRIBUTOR__5_GICD_SETSPI_NSR`. It includes the DMA headers in this work item (`dma_qm_0_regs.h` through `dma_qm_4_regs.h`, `dma_ch_3_regs.h`, `dma_ch_4_regs.h`, `dma_macro_regs.h`, `dma_nrtr_regs.h`, `dma_macro_masks.h`, `dma_qm_0_masks.h`, `dma_nrtr_masks.h`) and the MME/PLL/router headers.

Control flow: include-time composition only. Driver code includes `goya_regs.h` to gain a single namespace of register macros for initialization, security setup, CoreSight registration, queue programming, MMU/PCIe/PSOC handling, and diagnostics.

State and persistence: no runtime state. It defines compile-time constants that point at persistent hardware registers. Hardware persistence follows each referenced block.

Dependencies and integration: included directly by `goya_security.c` and `goya_coresight.c`, and indirectly by `goya_masks.h` used in `goya.c`. It is the primary integration point tying generated address maps to Goya driver implementation.

Risks: broad umbrella headers hide dependencies. A missing include can break distant driver code; a stale include can expose the wrong register layout. The local sync-manager and PCIe aliases are not in separate generated headers here, so they need the same scrutiny as generated definitions.

Test signals: full Goya driver compile, include-order checks, probe-time register accesses, sync-manager and interrupt tests, PCIe doorbell/device-ID reads, and runtime use by security and CoreSight setup paths.
