# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/Kconfig

Purpose: top-level Kconfig menu gate for QLogic/Brocade BR-series Ethernet devices.

Important APIs/types/functions: defines `config NET_VENDOR_BROCADE`, a boolean vendor selector defaulting to `y` when PCI is available. When enabled, it sources `drivers/net/ethernet/brocade/bna/Kconfig`, which exposes the actual `BNA` driver option.

Control flow: Kconfig evaluation first checks `depends on PCI`; if the vendor item is disabled, all child BR-series driver questions are skipped. If enabled, the BNA driver configuration is included.

State and persistence behavior: no runtime state. Persistent effect is the generated kernel `.config`, where `NET_VENDOR_BROCADE` controls visibility of child symbols.

Dependencies and integration points: integrates with the kernel networking vendor Kconfig hierarchy and depends on PCI support. It delegates driver-specific selection to the bna subdirectory.

Risks: changing the default, dependency, or `source` path can hide the BNA driver from configuration or expose it on unsupported non-PCI builds. The help text names QLogic BR-series cards, reflecting Brocade/QLogic branding.

Test signals: `make menuconfig` or `scripts/kconfig` should show the vendor menu under Ethernet drivers when PCI is enabled, and `CONFIG_BNA` should be reachable only when `NET_VENDOR_BROCADE=y`.
