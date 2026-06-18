# sources/distributed-fs/ceph-client/drivers/net/phy/Kconfig

## Purpose
Defines the PHY-layer Kconfig surface for phylib, phylink, SFP support, fixed PHY emulation, optional LED integration, Rust PHY abstractions, and individual Ethernet PHY drivers. The selected symbols determine which driver objects in this directory and its subdirectories are built and which helper infrastructure is available to MAC drivers and PHY drivers.

## Important APIs, Types, and Functions
This is declarative Kconfig rather than executable code. Important symbols include `PHYLINK`, `PHYLIB`, `SWPHY`, `PHY_PACKAGE`, `LED_TRIGGER_PHY`, `PHYLIB_LEDS`, `FIXED_PHY`, `RUST_PHYLIB_ABSTRACTIONS`, and `SFP`. Driver symbols in this work item include `AS21XXX_PHY`, `AIR_EN8811H_PHY`, `AMD_PHY`, `ADIN_PHY`, `ADIN1100_PHY`, `AQUANTIA_PHY` from the sourced Aquantia Kconfig, `AX88796B_PHY`, `AX88796B_RUST_PHY`, `BCM_CYGNUS_PHY`, `BCM_NET_PHYLIB`, and `BCM_NET_PHYPTP`.

## Control Flow and State
Runtime behavior is determined indirectly through dependency and select relationships. `PHYLINK` selects `PHYLIB` and `SWPHY`; `SFP` depends on I2C, PHYLINK, and compatible HWMON settings; `PHYLIB_LEDS` is enabled by OF when LED class support is compatible; Rust PHY support requires `RUST` and built-in `PHYLIB`. Individual driver symbols gate module/built-in compilation and helper library availability. There is no persistent runtime state in this file.

## Dependencies and Integration Points
The file integrates with the directory Makefile, kernel configuration front ends, and external subsystem symbols such as `LEDS_TRIGGERS`, `LEDS_CLASS`, `I2C`, `HWMON`, `RUST`, `PTP_1588_CLOCK_OPTIONAL`, `NETWORK_PHY_TIMESTAMPING`, `MACSEC`, SoC architecture symbols, and MDIO bus drivers. It sources vendor submenus for Aquantia, MediaTek, Qualcomm, and Realtek drivers.

## Risks and Test Signals
Risks are build-graph regressions: missing selects for helper libraries, impossible dependencies, Rust driver visibility when C fallback is expected, or enabling drivers without required MDIO/PTP/HWMON infrastructure. Test signals are `allmodconfig`, `allyesconfig`, `randconfig`, no-Rust and Rust-enabled builds, plus checking that each selected symbol results in the expected object from `drivers/net/phy/Makefile`.
