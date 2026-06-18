<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig

Purpose: declares the staging Kconfig option for the Xilinx AXI-Stream FIFO memory-mapped character driver.

Important APIs/types/functions: `config XIL_AXIS_FIFO` is a tristate option named `Xilinx AXI-Stream FIFO IP core driver`; it depends on `OF && HAS_IOMEM`.

Control flow: when selected, kbuild can compile `axis-fifo.o` from the matching Makefile.

State and persistence: stores only build configuration.

Dependencies and integration: depends on Device Tree probing and MMIO support because the driver is a platform driver using OF properties and mapped registers.

Risks: no explicit dependency on `MISC_DEVICES`, `DEBUG_FS`, or `POLL`-related facilities is needed because those are core APIs, but the driver's runtime ABI is a staging misc device and may change.

Test signals: Kconfig visibility on OF and non-OF builds, module/built-in builds, and compile with `COMPILE_TEST` style architectures that satisfy `HAS_IOMEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig -->
