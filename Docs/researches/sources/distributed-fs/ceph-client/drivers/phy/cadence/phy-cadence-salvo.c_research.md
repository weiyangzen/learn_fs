# sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-salvo.c

Purpose: Implements the Cadence SALVO legacy USB2/USB3 PHY driver for NXP platforms. It applies a fixed Cadence/NXP bring-up register sequence, tunes USB2 analog behavior, exposes power clock control, and handles a USB device-mode B-session-valid workaround.

Important APIs and types: `struct cdns_reg_pairs` represents 16-bit register/value pairs. `struct cdns_salvo_data` describes register stride and the init table. `struct cdns_salvo_phy` stores the PHY object, optional clock, MMIO base, match data, and USB2 disconnect threshold enum. PHY callbacks are `cdns_salvo_phy_init()`, `cdns_salvo_phy_power_on()`, `cdns_salvo_phy_power_off()`, and `cdns_salvo_set_mode()`.

Control flow: Probe gets match data for `nxp,salvo-phy`, obtains optional `salvo_phy_clk`, reads `cdns,usb2-disconnect-threshold-microvolt` with a 575 mV default, maps the MMIO resource, creates the PHY, and registers an OF provider. Init enables the clock, writes every USB3 register pair from the NXP sequence, sets receiver-detect slow clock, programs USB2 TXVALID gate timing, AFE RX register 5, and disconnect threshold, delays 10 us, then disables the clock. Power-on/off only prepare/enable or disable/unprepare the clock. Set-mode writes USB2 battery charger/session-valid register values for device mode versus other modes on NXP data.

State and persistence: The large init table is immutable. `usb2_disconn` persists the DT-selected threshold. Hardware register writes remain programmed after init; clock state is controlled by init and power callbacks.

Dependencies and integration points: Uses Linux PHY, platform, OF, optional clocks, bitfield helpers, and MMIO. It binds only `nxp,salvo-phy`. USB controller consumers invoke standard PHY init/power/mode calls.

Risks: `cdns_salvo_phy_init()` reads `TB_ADDR_TX_RCVDETSC_CTRL` into `value` but writes only `RXDET_IN_P3_32KHZ`, dropping any other bits in that register. USB2 disconnect threshold programming clears the mask and then assigns only `FIELD_PREP(...)`, also dropping unrelated bits from `UTMI_AFE_RX_REG0`; this may be intentional for documented reset values but is risky for future silicon. The fixed sequence has no readiness polling or error feedback beyond clock enable.

Test signals: Probe on `nxp,salvo-phy`, USB2 and USB3 enumeration, host/device role transitions invoking `.set_mode`, disconnect threshold validation across boards, clock enable reference behavior over repeated init/power cycles, and register dumps compared to Cadence/NXP reference values.
