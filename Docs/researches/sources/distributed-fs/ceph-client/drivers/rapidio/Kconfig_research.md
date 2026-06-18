# sources/distributed-fs/ceph-client/drivers/rapidio/Kconfig

Purpose: defines top-level RapidIO kernel configuration, including core subsystem enablement, optional enumeration, debug, DMA engine integration, channelized messaging, user-space mport character device access, and switch/device submenus.

Important options: `HAVE_RAPIDIO` is an architecture/platform capability boolean. `RAPIDIO` is the main tristate and depends on `HAVE_RAPIDIO || PCI`. `RAPIDIO_DISC_TIMEOUT` controls host discovery wait time. `RAPIDIO_ENABLE_RX_TX_PORTS` opts into enabling input/output ports for non-maintenance traffic. `RAPIDIO_DMA_ENGINE` depends on `DMADEVICES` and selects `DMA_ENGINE`. `RAPIDIO_DEBUG` adds debug messages through `subdir-ccflags`. `RAPIDIO_ENUM_BASIC`, `RAPIDIO_CHMAN`, and `RAPIDIO_MPORT_CDEV` enable fabric enumeration, channelized messaging, and `/dev` mport access. It sources device and switch Kconfig files.

Control flow and integration: this file drives which objects in the RapidIO Makefile are compiled. Because `RAPIDIO` is tristate, core code can be built in or as a module, and child drivers follow the selected symbols. `RAPIDIO_DMA_ENGINE` changes both generic mport cdev behavior and the Tsi721 device build by enabling DMA code paths.

State and persistence: no runtime state; Kconfig choices persist in the kernel build configuration and shape available ABI, modules, and debug output.

Dependencies: relies on Linux Kconfig, PCI, DMADEVICES, and RapidIO source layout. It includes `drivers/rapidio/devices/Kconfig` before later generic options, so device options are visible under the RapidIO menu.

Risks: enabling `RAPIDIO_MPORT_CDEV` exposes a broad user-space control surface for maintenance, mapping, DMA, and device add/remove operations. `RAPIDIO_ENABLE_RX_TX_PORTS` can change link behavior beyond maintenance traffic. The help text for DMA contains a typo but no functional effect.

Test signals: run `make menuconfig` or `scripts/kconfig/conf` combinations with `RAPIDIO=y/m`, `PCI=n`, and `DMADEVICES` toggles; verify object inclusion matches the Makefiles and that `RAPIDIO_DEBUG` adds `-DDEBUG`.
