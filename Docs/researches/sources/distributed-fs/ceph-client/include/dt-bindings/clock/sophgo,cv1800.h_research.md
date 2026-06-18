# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,cv1800.h

## Purpose
`sophgo,cv1800.h` defines clock IDs for Sophgo CV1800-family clock providers.

## Important APIs, types, and functions
All exported IDs use `CLK_*`. The namespace begins with PLLs (`CLK_MPLL`, `CLK_TPLL`, `CLK_FPLL`, `CLK_MIPIMPLL`, `CLK_A0PLL`, display/camera PLLs), derived PLL divisors, TPU, buses, AXI/AHB/APB clocks, video/camera/display blocks, audio, UART/I2C/SPI/PWM/GPIO, timers, watchdog, USB, Ethernet, SD/eMMC, crypto, sensor/image pipelines, CPU-related clocks (`CLK_C906_*`, `CLK_A53`, `CLK_CPU_AXI0`, `CLK_CPU_GIC`), and reference outputs.

## Control flow
The header has no functions. DTS files use these IDs in clock specifiers, and the Sophgo CV1800 clock driver maps them to gates, dividers, muxes, and PLLs.

## State and persistence
No state exists in the header. Numeric IDs are persistent ABI. Runtime state resides in CV1800 clock-controller registers and may be seeded by boot firmware.

## Dependencies and integration points
It integrates with Sophgo CV1800 DTS, the CV1800 clock driver, RISC-V/Arm CPU clock consumers depending on variant, TPU/NPU-style acceleration, image/video/display pipelines, storage, Ethernet, USB, serial buses, and watchdog/timer blocks.

## Risks and test signals
Risks include SoC-variant mismatches, clock IDs for CPU architectures not present on a board, and media pipeline clocks with tight parent/rate requirements. Test signals include DT validation, clock provider probe, console/storage/network boot, watchdog/timer operation, camera/display pipeline tests, and clk-summary verification of PLL-derived rates.
