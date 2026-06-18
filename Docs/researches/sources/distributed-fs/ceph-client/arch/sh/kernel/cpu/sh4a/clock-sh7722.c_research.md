# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/clock-sh7722.c

## Purpose
`clock-sh7722.c` registers SH7722 clocks, including div4 enable/reparent clocks for IRDA and SIU audio clocks in addition to normal root/divider/MSTP clocks.

## Important APIs, Types, And Functions
It defines `r_clk`, `extal_clk`, `dll_clk`, `pll_clk`, `main_clks`, `div4_clks`, `div4_enable_clks`, `div4_reparent_clks`, `div6_clks`, `mstp_clks[HWBLK_NR]`, `lookups`, and `arch_clk_init()`.

## Control Flow
`arch_clk_init()` registers main clocks, installs lookups, registers div4 clocks, div4-enable clocks, div4-reparent clocks, div6 clocks, and MSTP gates in order. Drivers then acquire clocks by device IDs such as `sh-sci.0`, `sh-tmu.0`, `sh-cmt-32.0`, `sh_mobile_sdhi.0`, and LCDC.

## State And Persistence
Clock state lives in FRQCR, VCLKCR, SCLKACR/BCR, IRDACLKCR, PLL/DLL registers, and MSTPCR bits. The static lookup table is the software binding contract.

## Dependencies And Integration Points
It integrates with the SH mobile clock helpers, setup/board platform devices, and drivers for serial, timers, watchdog, flash, SDHI, USBF, audio, camera, video, and LCDC.

## Risks
Registration order matters because reparent clocks require parents to exist. HWBLK indexes must align with `clock-sh7722.h` style enumerations used by devices. Lookup-name drift breaks clock acquisition.

## Test Signals
Driver probe success across timers/serial/SDHI/USB/display/audio, clock tree inspection, and suspend/resume clock gating tests are strong signals.
