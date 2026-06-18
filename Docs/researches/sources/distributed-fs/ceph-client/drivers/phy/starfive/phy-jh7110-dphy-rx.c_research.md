# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-rx.c

Purpose: StarFive JH7110 MIPI D-PHY RX provider that configures lane enable/swap and clock pre-counters for receive-side MIPI operation.

Important APIs, types, and functions: `struct stf_dphy_info` holds six lane mapping entries. `struct stf_dphy` stores MMIO registers, cfg/ref/tx clocks, reset array, 0.9 V regulator, PHY, and match data. `stf_dphy_configure()` writes lane enables, lane swap, PLL clock select, and pre-counter fields. Power ops manage runtime PM, regulator, clock rates, and resets.

Control flow: probe maps resource 0, gets clocks `cfg`, `ref`, `tx`, reset array, regulator `mipi_0p9`, creates PHY, enables runtime PM, and registers simple xlate. Power-on resumes runtime PM, enables regulator, sets fixed clock rates (99 MHz, 49.5 MHz, 19.8 MHz), and deasserts reset. Power-off asserts reset, disables regulator, and drops runtime PM. Configure writes static timing and lane mapping values from match data.

State and persistence: lane mapping is constant per compatible. Hardware state persists in syscfg registers while powered. No configuration cache is kept.

Dependencies and integration points: generic PHY MIPI D-PHY consumers, PM runtime, regulator, clock/reset frameworks, compatible `starfive,jh7110-dphy-rx`.

Risks: clock rate set return values are ignored, so unsupported rates may go unnoticed. Runtime PM is enabled without a remove disable path. Configure does not validate `opts` mode or lane count.

Test signals: CSI receiver bring-up, lane mapping validation, regulator and runtime PM balance, clock rate readback, and MIPI D-PHY consumer configure sequences.
