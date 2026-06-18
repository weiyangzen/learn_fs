# sources/distributed-fs/ceph-client/arch/sh/drivers/Makefile



Source read size: 10 lines, 240 bytes.



Purpose: top-level SH driver object selection.

Important APIs/types/functions: always builds `dma/` and `platform_early.o`; conditionally builds `pci/`, `push-switch.o`, and `heartbeat.o`.

Control flow: Kbuild descends into driver subdirectories according to architecture and feature symbols.

State and persistence: build graph only.

Dependencies and integration points: integrates Kconfig symbols with SH platform, PCI, DMA, and board support code.

Risks and test signals: unconditional `dma/` directory descent still relies on subdirectory symbols. Test SH allnoconfig/defconfig/allmodconfig builds.
