# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Kconfig

Purpose: Microchip KSZ DSA build options for the common switch core, transports, optional PTP, and KSZ8863 SMI support.

Important APIs/types/functions: `NET_DSA_MICROCHIP_KSZ_COMMON` selects DSA taggers, IEEE 802.1Q helpers, DCB, and XPCS. Transport symbols cover I2C, SPI, and SMI. `NET_DSA_MICROCHIP_KSZ_PTP` gates timestamp/PTP support on newer chips.

Control flow: no runtime flow; configuration controls built objects and selected dependencies.

State and persistence: no runtime state; persistent effect is kernel config.

Dependencies and integration: common depends on `NET_DSA`; I2C/SPI depend on bus frameworks and select regmap support; SMI selects `MDIO_BITBANG`; PTP has `PTP_1588_CLOCK` consistency constraints.

Risks and test signals: broad common coverage, missing dependencies, or module/built-in PTP mistakes. Test common-only, SMI, I2C, SPI, and PTP-enabled builds.
