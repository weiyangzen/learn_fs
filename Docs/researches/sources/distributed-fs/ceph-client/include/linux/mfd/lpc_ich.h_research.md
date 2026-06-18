# Research: sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h

**Purpose:** Provides the compact platform-description ABI for Intel ICH/PCH LPC bridge MFD support, especially watchdog, GPIO, GPE0, and Intel SPI child resources.

**Important APIs and types:** Defines GPIO resource indexes `ICH_RES_GPIO` and `ICH_RES_GPE0`, GPIO hardware-generation enum `lpc_gpio_versions`, forward-declared `struct lpc_ich_gpio_info`, and `struct lpc_ich_info` with name, TCO watchdog version, GPIO version/info, SPI type, and GPIO enable flag. Exports `lpc_ich_gpio_swnode`.

**Control flow:** PCI ID tables in the LPC ICH MFD driver select an `lpc_ich_info` entry, then child platform devices consume the encoded watchdog/GPIO/SPI capabilities and software node.

**State and persistence:** This header defines static hardware-description state only. Runtime persistence is in the parent device and child drivers; no mutable data is declared here.

**Dependencies and integration:** Depends on `linux/platform_data/x86/spi-intel.h` for `enum intel_spi_type` and on software nodes for GPIO child description.

**Risks:** The `use_gpio` byte and generation enum must match platform quirks. Wrong `spi_type` or GPIO version can expose invalid register layouts. Resource index macros are positional and must stay aligned with parent resource creation.

**Test signals:** Compile tests for LPC ICH and Intel SPI combinations, probe tests for representative chipset entries, and validation that GPIO software-node consumers bind only when `use_gpio` and `gpio_info` are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h -->
