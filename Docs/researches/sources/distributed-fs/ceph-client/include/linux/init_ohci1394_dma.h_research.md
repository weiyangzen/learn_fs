<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h

Purpose: Declares optional early OHCI-1394 DMA initialization hooks.

Important APIs/types/functions: When `CONFIG_PROVIDE_OHCI1394_DMA_INIT` is enabled, exposes `init_ohci1394_dma_early` initdata flag and `init_ohci1394_dma_on_all_controllers()`.

Control flow: Early boot code can inspect the flag and initialize DMA on all OHCI-1394 controllers.

State/persistence: The flag is `__initdata`, so it is only meaningful during init. Controller DMA state is external hardware state.

Dependencies/integration: Depends on init annotations and the optional FireWire/OHCI early DMA provider.

Risks: Only available under the Kconfig option; code must not reference symbols otherwise.

Test signals: Kconfig enabled/disabled builds and early boot path coverage on systems with OHCI-1394 controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h -->
