## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Makefile

Purpose: top-level build hook for aQuantia Ethernet drivers.

Important APIs/types: single kbuild assignment `obj-$(CONFIG_AQTION) += atlantic/`.

Control flow: no runtime behavior. During kernel build, selecting `CONFIG_AQTION` recurses into the Atlantic subdirectory.

State and persistence: build metadata only.

Dependencies/integration: consumes the `AQTION` Kconfig symbol and delegates object composition to `atlantic/Makefile`.

Risks: minimal; wrong symbol or path would prevent the driver from building.

Test signals: `make M=drivers/net/ethernet/aquantia` includes the Atlantic subtree when `CONFIG_AQTION` is enabled.
