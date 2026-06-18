# sources/distributed-fs/ceph-client/drivers/phy/microchip/lan966x_serdes_regs.h

Purpose: Provides generated-style LAN966x HSIO register address macros and bitfield helpers used by `lan966x_serdes.c`.

Important APIs, types, and flow: Defines `enum lan966x_target` with `TARGET_HSIO`, address tuple macros such as `HSIO_SD_CFG(g)`, `HSIO_MPLL_CFG(g)`, `HSIO_SD_STAT(g)`, `HSIO_HW_CFG`, `HSIO_RGMII_CFG(r)`, and `HSIO_DLL_CFG(r)`, and field `*_SET()`/`*_GET()` wrappers built from `FIELD_PREP()` and `FIELD_GET()`. Covered fields include SD lane resets/rates/inversion/data enables/loopback, MPLL enable/refclk/multiplier, status bits, HSIO mux config for RGMII/SD6G/GMII/QSGMII, RGMII clock/reset, and DLL delay enable/reset.

State, dependencies, and integration points: This header carries no state; it is the compile-time register contract for LAN966x SerDes programming. The tuple layout is consumed by `lan_offset()` in the C file to compute byte offsets.

Risks and test signals: Incorrect tuple dimensions or bit masks would silently write the wrong HSIO register or field. Compile-time users should remain limited to compatible address macros, and hardware tests should verify each field against the datasheet through known-good mode transitions and status polling.
