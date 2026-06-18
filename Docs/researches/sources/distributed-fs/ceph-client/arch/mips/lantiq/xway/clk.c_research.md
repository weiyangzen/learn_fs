# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/clk.c

Purpose: derives CPU, FPI/OCP, and PPE/PP32 clock rates for XWAY-family Lantiq SoCs from CGU registers.

Important APIs/functions: `ltq_danube_cpu_hz`, `ltq_danube_fpi_hz`, `ltq_danube_pp32_hz`, `ltq_ar9_cpu_hz`, `ltq_ar9_fpi_hz`, `ltq_vr9_cpu_hz`, `ltq_vr9_fpi_hz`, `ltq_vr9_pp32_hz`, `ltq_ar10_cpu_hz`, `ltq_ar10_fpi_hz`, `ltq_ar10_pp32_hz`, `ltq_grx390_cpu_hz`, `ltq_grx390_fpi_hz`, and `ltq_grx390_pp32_hz`.

Control flow: each function reads `ltq_cgu_r32()` at SoC-specific offsets, decodes selector/divider bitfields, and returns a fixed frequency constant or divided frequency. Danube derives CPU/FPI from DDR clock, newer XRX paths use `CGU_SYS_XRX` and `CGU_IF_CLK_AR10`.

State and persistence: stateless; all state comes from CGU hardware registers.

Dependencies and integration: declared in `clk.h` and consumed by `xway/sysctrl.c` when registering static clocks.

Risks: unknown selector values often return `0` or a default rate. Some comments note unresolved XTAL-frequency assumptions elsewhere.

Test signals: boot-time CPU clock print, measured timer frequency, and per-SoC CGU selector coverage.
