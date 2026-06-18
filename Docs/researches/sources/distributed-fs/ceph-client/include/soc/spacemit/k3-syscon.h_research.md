# sources/distributed-fs/ceph-client/include/soc/spacemit/k3-syscon.h

Purpose: defines SpacemiT K3 clock/reset syscon register offsets and PLL lock bits across APBS, MPMU, APBC, APMU, DCIU, RCPU SYSCTRL/UART/I2S/SPI/I2C/PWM/RPMU, and APBC2 SEC domains.

Important APIs/types/functions: macro-only API including eight PLL SWCR groups, `POSR_PLL1_LOCK` through `POSR_PLL8_LOCK`, large APBC/APMU peripheral offset sets, DCIU DMA reset/clock offsets, RCPU peripheral clock/reset offsets, and APBC2 SEC offsets. It includes `ccu.h`.

Control flow: K3 clock and reset drivers index SoC-specific clock/reset descriptors with these offsets, write through regmap, and poll PLL lock state where needed.

State and persistence: hardware clock, reset, PLL, and domain-control state persists in syscon registers until reset or later reconfiguration.

Dependencies and integration: included by `drivers/clk/spacemit/ccu-k3.c`, `drivers/reset/spacemit/reset-spacemit-k3.c`, and shared SpacemiT CCU/reset code.

Risks: K3 has a broad register surface; copied K1 names with changed offsets can create subtle peripheral failures. Duplicate-looking domains require correct reset-controller mapping. Test signals include K3 clock registration, reset-line enumeration, peripheral probe coverage, PLL lock checks, and boot smoke tests with clocks enabled/disabled.
