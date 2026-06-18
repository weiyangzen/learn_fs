## sources/distributed-fs/ceph-client/include/linux/mfd/da8xx-cfgchip.h

Purpose: This header defines TI DaVinci DA8xx `CFGCHIP` syscon register offsets and bitfields for consumers configuring PLL/EDMA, capture routing, USB PHY, EMAC/uPP/PRU, and McASP mute behavior.

Important APIs, types, and constants: `CFGCHIP(n)` converts a CFGCHIP register index into a 32-bit offset. CFGCHIP0 bits cover PLL0 master lock and EDMA3_0 transfer-controller default burst sizes. CFGCHIP1 bits cover eCAP source selection for three capture modules, HPI byte/address behavior, HPI enable, EDMA3_1 burst size, eHRPWM TBCLK sync, and McASP0 AMUTE source selection. CFGCHIP2 bits cover USB PHY clock-good, VBUS sense, reset, OTG mode override, PHY clock muxes, power-down, suspend, PLL, session/VBUS detection, and reference frequency. CFGCHIP3 bits cover RMII selection, uPP TX clock source, PLL1 lock, async clock, PRU event select, divider enable, and EMIFA clock source. CFGCHIP4 has McASP AMUTE clear.

Control flow: No functions exist. Syscon consumers combine masks and values with regmap updates to configure SoC-level muxes and PHY modes before enabling peripheral drivers.

State and persistence: Register state is SoC system-controller state and may survive peripheral driver unbind until reset or explicit reconfiguration.

Dependencies and integration points: Includes `linux/bitops.h`; integrates with syscon/regmap users in USB PHY, PWM/eCAP, EDMA, audio/McASP, networking, PRU, and clock/reset paths.

Risks: Several macros are named `CFGCHIP0_EDMA31...` inside the CFGCHIP1 section, which is historically confusing. These are global SoC controls; wrong updates can break unrelated peripherals. Field values must be masked before writes to avoid clobbering neighboring muxes.

Test signals: Consumer driver tests should verify regmap update masks, USB host/device OTG mode selection, reference-clock choices, eCAP routing, EDMA burst configuration, and no unexpected changes in unrelated CFGCHIP fields.
