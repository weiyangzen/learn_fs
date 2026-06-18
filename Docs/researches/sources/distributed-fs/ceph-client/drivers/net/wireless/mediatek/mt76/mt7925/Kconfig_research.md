# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Kconfig

Purpose: Kconfig declarations for the MT7925 Wi-Fi 7 driver family. It separates common code from PCIe and USB front ends.

Important APIs/types/functions: `MT7925_COMMON` is a hidden tristate selecting `MT792x_LIB` and `WANT_DEV_COREDUMP`. `MT7925E` enables PCIe support and depends on `MAC80211` and `PCI`. `MT7925U` enables USB support, selects `MT792x_USB`, and depends on `MAC80211` and `USB`.

Control flow: build selection is user-facing for PCIe/USB modules. Selecting either bus driver selects the common MT7925 core; USB additionally pulls the MT792x USB support library.

State/persistence: no runtime state. Persistent effect is kernel build configuration and module availability.

Dependencies/integration: integrates with the mt76 Kconfig hierarchy, mac80211, PCI, USB, common MT792x library, and devcoredump support.

Risks: SDIO is not exposed for MT7925 in this file; adding one would require new config and Makefile objects. Common code always selects devcoredump, increasing dependency surface. Bus symbols must stay aligned with objects in `Makefile`.

Test signals: `allyesconfig`, modular PCIe-only, USB-only, and disabled builds should select the expected objects and avoid unresolved symbols.
