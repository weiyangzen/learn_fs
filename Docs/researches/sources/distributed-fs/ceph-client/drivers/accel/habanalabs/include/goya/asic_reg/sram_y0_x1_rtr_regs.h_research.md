# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/sram_y0_x1_rtr_regs.h

Purpose: maps the SRAM row-0 X1 router register set. It is structurally identical to X0 but shifted to the X1 address range, defining HBW/LBW read, data, write-response, max-credit, and debug arbiter registers.

Important APIs/types/functions: macro-only `mmSRAM_Y0_X1_RTR_*` definitions from `0x205100` through `0x205330`, with 30 offsets and E/W/local direction suffixes.

Control flow: callers can compute tiled router addresses or use these explicit macros to configure and inspect the X1 SRAM interconnect router. Sequencing is external to the header.

State and persistence: register values persist in the SRAM router hardware and influence routing/arbitration until reset or update.

Dependencies and integration: included by `goya_regs.h`. The offset delta from X0 is part of the tiled SRAM-bank model and is used by adjacent hardware headers and block-base definitions.

Risks: because the five X routers are nearly identical, copy/paste mistakes in base addresses are easy and can silently configure a neighboring router. Directional field availability must match the hardware topology.

Test signals: per-bank SRAM traffic tests, X0/X1 offset-delta checks, router debug counter reads, and interconnect stress with traffic targeting X1-backed SRAM.
