# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc85xx.h

Purpose: defines MPC85xx/QorIQ system version register decoding helpers and SoC version constants.

Important APIs/types/functions: `SVR_REV`, `SVR_MAJ`, `SVR_MIN`, and `SVR_SOC_VER` extract revision and SoC identity. Constants enumerate many 85xx, P-series, T-series, C29x, B/G-series, 86xx, and unknown SVR values.

Control flow: platform detection reads the hardware SVR, applies `SVR_SOC_VER()` and revision helpers, and compares against constants to select errata/workarounds or board behavior.

State and persistence: no state; SVR is read from CPU/SoC hardware elsewhere.

Dependencies and integration points: used by Freescale/QorIQ platform setup, CPU detection, errata handling, and device initialization.

Risks: incorrect constants or masks misidentify SoCs and can enable wrong errata workarounds. Some constants use uppercase `0X` but remain valid C constants.

Test signals: boot each supported SoC family where available, verify `/proc/cpuinfo`/platform detection, errata selection, and build-time users of every SVR constant.
