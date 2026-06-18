# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/sram_y0_x4_rtr_regs.h

Purpose: defines the SRAM row-0 X4 router register addresses. It is the fifth row-0 SRAM router map in this subset and covers the same HBW/LBW arbitration and debug surface as X0 through X3.

Important APIs/types/functions: `mmSRAM_Y0_X4_RTR_*` macros span `0x211100` to `0x211330`. The 30 definitions include `HBW_RD_RQ_*_ARB`, `HBW_*_ARB_MAX`, `HBW_DATA_*_ARB`, `HBW_WR_RS_*_ARB`, and the LBW/debug equivalents for E/W/local directions.

Control flow: external setup code writes arbitration/max-credit registers and diagnostic code reads debug registers. The header only provides addresses.

State and persistence: SRAM interconnect arbitration settings are retained in hardware until reset or reprogramming.

Dependencies and integration: included by `goya_regs.h` and tied to tiled SRAM block definitions. It follows the same generated prototype as the other row-0 SRAM routers.

Risks: edge router topology assumptions must be verified; using a nonexistent direction or wrong bank base can misprogram the fabric. Uniform names also make accidental X3/X4 substitution plausible.

Test signals: X4-targeted SRAM traffic, router debug readback, generated address-stride checks, and full-fabric stress with all SRAM banks active.
