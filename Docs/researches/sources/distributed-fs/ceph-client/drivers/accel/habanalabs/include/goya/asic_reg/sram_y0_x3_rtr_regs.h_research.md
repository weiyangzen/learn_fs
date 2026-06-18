# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/sram_y0_x3_rtr_regs.h

Purpose: maps the SRAM row-0 X3 router block. It supplies explicit addresses for HBW/LBW read request, data, write response, max credit, and debug arbitration registers.

Important APIs/types/functions: macro-only `mmSRAM_Y0_X3_RTR_*` constants from `0x20D100` through `0x20D330`. It has the same 30-register shape as X0..X2 and X4.

Control flow: external driver or firmware routines use the macros for SRAM interconnect tuning and diagnostics. There is no local executable flow.

State and persistence: all meaningful state is in the router hardware; settings persist across driver calls and affect SRAM fabric behavior.

Dependencies and integration: included through `goya_regs.h` and aligned with block definitions in `goya_blocks.h`. The regular address stride supports indexed access patterns.

Risks: the uniform map can hide address transposition errors. A wrong X3 definition may only appear under traffic patterns that target the corresponding SRAM bank or path.

Test signals: per-bank SRAM access, HBW/LBW arbitration stress, debug arbiter max-credit readback, and generated-header consistency checks against X0/X1/X2/X4.
