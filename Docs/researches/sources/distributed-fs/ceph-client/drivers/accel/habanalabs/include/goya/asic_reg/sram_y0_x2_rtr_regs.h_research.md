# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/sram_y0_x2_rtr_regs.h

Purpose: defines the SRAM row-0 X2 interconnect router register map. It provides the same 30 HBW/LBW arbitration, max-credit, data, write-response, and debug registers as the neighboring SRAM routers.

Important APIs/types/functions: exported macros are `mmSRAM_Y0_X2_RTR_*`, spanning `0x209100` to `0x209330`. The register names identify E/W/local arbitration paths and HBW/LBW classes.

Control flow: low-level configuration code writes arbitration weights or max credits, while diagnostics can read debug arbiter registers. The header is a declarative address source only.

State and persistence: hardware registers keep router arbitration state. Values persist until reset or another programming pass.

Dependencies and integration: included by `goya_regs.h`; it belongs to the tiled SRAM router family and follows the same `0x4000` spacing as adjacent X positions.

Risks: incorrect X2 offsets can skew middle-bank SRAM routing and are hard to diagnose because traffic may still work with degraded fairness or timeouts. Tests should not assume all X routers share a single base unless the block map confirms it.

Test signals: SRAM bank X2 throughput, concurrent HBW/LBW pressure, router debug register reads, and address-map audits comparing X0..X4 spacing.
