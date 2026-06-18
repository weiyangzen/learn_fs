# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-emmc.c

## Purpose
This driver controls the RK3399 eMMC PHY through GRF registers. It powers the analog block, calibrates pads, configures DLL frequency range, output tap delay, strobe pulldown, and drive impedance for the eMMC controller.

## Important APIs, Types, And Functions
`struct rockchip_emmc_phy` stores GRF offset/base, optional `emmcclk`, and DT-configured electrical parameters. `rockchip_emmc_phy_power()` performs the shared power-off/power-on sequence, polling CALDONE and DLLRDY. `rockchip_emmc_phy_init()` intentionally gets `emmcclk` late to avoid a circular dependency with the SDHCI clock provider. `rockchip_emmc_phy_power_on()` writes drive impedance, tap delay, and strobe settings before powering the analog block. `convert_drive_impedance_ohm()` maps DT ohm values to hardware codes.

## Control Flow
Probe obtains the parent GRF syscon, reads the child `reg` offset, applies defaults and optional DT properties, creates the PHY, and registers a simple provider. Init obtains the optional eMMC clock. Power-on first programs electrical tuning registers, then forces PDB/ENDLL low, checks the current card clock rate to choose DLL frequency, powers up calibration, polls for CALDONE, enables the DLL, and polls for DLLRDY unless the clock rate is zero. Power-off drives PDB and ENDLL low.

## State And Persistence
Persistent software state is the DT-derived tuning configuration and the late-acquired clock pointer. Hardware state remains in GRF registers until reset or power-off. The clock pointer is released in `.exit`.

## Dependencies And Integration Points
It depends on generic PHY, parent syscon GRF, optional `emmcclk`, platform DT properties `drive-impedance-ohm`, `rockchip,enable-strobe-pulldown`, and `rockchip,output-tapdelay-select`, and compatible `rockchip,rk3399-emmc-phy`. It is used by the MMC/SDHCI controller through a PHY phandle.

## Risks And Test Signals
The late clock lookup is intentional but unusual; failures surface at PHY init rather than probe. DLL lock can take longer than documentation, so polling timeout regressions affect high-speed eMMC modes. Test signals include valid/invalid DT impedance mapping, zero-rate init path, CALDONE and DLLRDY polling, HS200/HS400 tuning stability, and clean clock put on exit.
