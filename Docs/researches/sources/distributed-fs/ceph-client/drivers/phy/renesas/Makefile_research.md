# sources/distributed-fs/ceph-client/drivers/phy/renesas/Makefile

Purpose: Maps Renesas PHY Kconfig symbols to driver object files.

Important APIs/types/functions: Builds `r8a779f0-ether-serdes.o`, `phy-rcar-gen2.o`, `phy-rcar-gen3-pcie.o`, `phy-rcar-gen3-usb2.o`, `phy-rcar-gen3-usb3.o`, and `phy-rzg3e-usb3.o` according to their respective config symbols.

Control flow: No runtime logic. Kbuild includes objects based on config values.

State and persistence: No runtime state beyond build outputs.

Dependencies and integration points: Integrates with `drivers/phy/renesas/Kconfig` and parent PHY build rules.

Risks: A config/object typo breaks builds or silently omits platform support. This file includes objects not otherwise researched in this subset, so changes should account for the whole Renesas PHY directory.

Test signals: Enable each config as module or built-in where supported and verify expected object/module generation.
