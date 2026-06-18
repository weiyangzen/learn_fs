# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/sram_y0_x0_rtr_regs.h

Purpose: maps the first SRAM row-0 router block at X0. It defines 30 offsets for HBW and LBW read request arbitration, max credits, data arbitration, write response arbitration, and debug arbiter/max-credit registers.

Important APIs/types/functions: macro-only `mmSRAM_Y0_X0_RTR_*` definitions from `0x201100` through `0x201330`. Direction suffixes are `E`, `W`, and `L`, matching east/west/local router ports for this position.

Control flow: router setup or diagnostics reads/writes these offsets relative to the SRAM router block to tune arbitration and inspect debug credits. No code runs inside the header.

State and persistence: arbitration and debug register values are SRAM interconnect hardware state and persist until reset or reconfiguration.

Dependencies and integration: included by `goya_regs.h`; block bases and spacing are in `goya_blocks.h`. Equivalent Gaudi code uses `SRAM_BANK_OFFSET` derived from X1 minus X0 bases, illustrating how these tiled router maps support indexed access.

Risks: X0 has only E/W/local directions in this generated map; assuming north/south fields from other router prototypes would address nonexistent registers. Wrong offsets can affect SRAM traffic arbitration and cause performance or timeout issues.

Test signals: SRAM bandwidth tests, router credit/debug reads, stress under simultaneous DMA/TPC/MME traffic, and reset default checks.
