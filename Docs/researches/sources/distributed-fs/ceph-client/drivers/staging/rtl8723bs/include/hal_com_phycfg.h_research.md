# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_com_phycfg.h

Purpose: this header defines shared PHY configuration types and declarations for TX power by rate, TX power limits, RF path register definitions, and channel-plan-to-regulation conversion.

Important APIs/types/macros: path constants `PathA` through `PathD`, `enum rate_section` (`CCK`, `OFDM`, `HT_MCS0_MCS7`), `MAX_POWER_INDEX`, and power-limit regulation IDs are defined. `struct bb_register_def` maps per-RF-path BB register addresses for RF interface software control, output, enable, 3-wire offset, HSSI parameter, and LSSI readback. Function declarations cover TX power base/rate index lookup, storing/configuring TX power by rate, setting power by path/rate array, power-limit initialization/conversion, `phy_get_tx_pwr_lmt`, tracking offsets, and `Hal_ChannelPlanToRegulation`.

Control flow and integration: `rtl8723b_phycfg.c` fills `hal_com_data.PHYRegDef` using this struct, then callers use it for RF serial operations. TX power parsing in `rtl8723b_hal_init.c` populates `hal_com_data`; PHY functions declared here consume that data to program hardware power indexes.

State and persistence: the declarations operate on `hal_com_data` power tables and RF register definitions. Actual persistent runtime values are held in the adapter HAL data and hardware registers.

Dependencies: depends on `struct adapter`, channel-width enums, and RF path/rate constants from surrounding driver headers.

Risks and test signals: RF path argument ordering must match implementations; `PHY_GetTxPowerTrackingOffset` declaration uses `Rate, RFPath` while some callers pass `RFPath, Rate` in the implementation context, which deserves compile/signature review. Tests should validate per-rate power indexes, regulatory limits, channel-plan regulation mapping, and RF path A/B register definitions.
