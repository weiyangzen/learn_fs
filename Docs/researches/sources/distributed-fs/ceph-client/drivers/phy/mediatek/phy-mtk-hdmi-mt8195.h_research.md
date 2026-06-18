<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h

Purpose: Defines MT8195 HDMI PHY register offsets, bitfields, and PLL constants used by `phy-mtk-hdmi-mt8195.c`.

Important APIs and types: Exposes macros such as `PCW_DECIMAL_WIDTH`, `PLL_PREDIV`, `PLL_FBKDIV_HS3`, HDMI config register offsets, PLL field masks, driver impedance/bias fields, FIFO enable, 5 V output bit, and pixel clock selection fields.

Control flow: No executable logic. The macros feed `mtk_phy_update_field()` and bit operations in the MT8195 implementation.

State and persistence: No software state. The masks define persistent MMIO fields for PLL, analog, TMDS, FRL, and regulator behavior.

Dependencies and integration points: Included only by the MT8195 HDMI PHY implementation. Depends on Linux bitfield macros and types.

Risks: Incorrect masks or offsets directly misprogram analog/PLL hardware and are not validated by the compiler beyond constant expression checks in field helpers. Names encode HDMI TX 2.1/20 hardware details, so reuse for another SoC would be risky.

Test signals: Compile coverage, register writes matching vendor reference values, PLL set-rate across all divider cases, and readback of power/clock/regulator bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi-mt8195.h -->
