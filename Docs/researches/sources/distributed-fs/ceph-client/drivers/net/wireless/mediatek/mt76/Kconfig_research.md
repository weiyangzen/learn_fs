# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Kconfig

Purpose: defines core mt76 Kconfig symbols and sources per-chip mt76 family configuration. It separates shared core, transport, library, LED, NPU, and chipset-specific options.

Important APIs/types/functions: defines `MT76_CORE` as a hidden tristate selecting `PAGE_POOL`; `MT76_LEDS` with LED class dependency and default; transport symbols `MT76_USB` and `MT76_SDIO`; shared library symbols `MT76x02_LIB`, `MT76x02_USB`, `MT76_CONNAC_LIB`, `MT792x_LIB`, `MT792x_USB`; and `MT76_NPU`. It sources Kconfig files for `mt76x0`, `mt76x2`, `mt7603`, `mt7615`, `mt7915`, `mt7921`, `mt7996`, and `mt7925`.

Control flow: chip-specific drivers select the shared library and transport symbols they need. Enabling a chip driver pulls in `MT76_CORE`, which in turn selects `PAGE_POOL`, making the common DMA/RX code available. Optional LED and NPU support are gated by their own symbols.

State and persistence: persists only through kernel configuration symbols. There is no runtime code in this file.

Dependencies and integration: integrated with kbuild through the sibling Makefile and with Linux subsystems through `PAGE_POOL`, `LEDS_CLASS`, PCI/USB/SDIO symbols in child Kconfigs, and optional NPU support.

Risks: hidden library symbols must be selected correctly by child drivers; otherwise builds can miss shared objects. The LED dependency expression must stay compatible with built-in/module combinations. Adding a new chipset requires sourcing its Kconfig and adding Makefile object rules.

Test signals: configuration tests should cover built-in and module combinations for core, LED class, USB/SDIO transport, NPU, and each sourced chipset family. Kconfig linting should catch unmet dependency chains.
