# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-ahci.c

Purpose: generic PHY provider for UniPhier AHCI/SATA PHY blocks on Pro4, PXs2, and PXs3 SoCs.

Important APIs, types, and functions: `struct uniphier_ahciphy_priv` stores MMIO, clocks, resets, and SoC data. `struct uniphier_ahciphy_soc_data` supplies optional init/power callbacks and flags. Pro4 routines program MPLL/RX/TX parameters and manage PM/TX/RX resets; PXs2/PXs3 routines toggle `CKCTRL_REF_SSP_EN`/`CKCTRL_P0_RESET` and poll PLL ready. Generic `phy_ops` provide `.init`, `.exit`, `.power_on`, `.power_off`.

Control flow: probe maps one MMIO resource, obtains link and optional PHY/GIO clocks and resets depending on SoC flags, creates a single PHY, and registers simple xlate. `.init` enables parent GIO/link clocks, deasserts parent resets, and runs optional SoC parameter programming. `.power_on` enables the PHY clock when present, deasserts PHY reset, and runs SoC power-on. Error paths assert resets and disable clocks in reverse. `.power_off` runs SoC shutdown, asserts PHY reset, and disables PHY clock.

State and persistence: state is private per PHY. Hardware state persists in AHCI PHY registers and reset lines. `is_ready_high` changes PLL-ready polarity for PXs2 versus PXs3; `is_phy_clk` controls whether a dedicated PHY clock is managed.

Dependencies and integration points: generic PHY, clock/reset APIs, MMIO polling, platform DT compatibles `socionext,uniphier-*-ahci-phy`, and AHCI controller consumers.

Risks: PXs3 init appears to prepare TXCTRL1/RXCTRL values but does not visibly write them after modification, which may be intentional omission or a latent bug. Poll timeouts are short for PXs2/PXs3. Legacy Pro4 has multiple shared resets and clocks; any mismatch in DT reset names breaks probe.

Test signals: boot probe for each compatible, SATA link training at Gen speeds, PLL-ready timeout logs, suspend/resume power cycling, and register trace comparing PXs3 parameter writes with hardware programming expectations.
