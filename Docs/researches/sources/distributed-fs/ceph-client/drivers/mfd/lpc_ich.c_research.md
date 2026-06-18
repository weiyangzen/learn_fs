# sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c

Purpose: this PCI MFD driver binds Intel ICH/PCH LPC bridge functions and exposes embedded watchdog, GPIO/pinctrl, and SPI flash controller devices. It covers a large PCI ID matrix from early ICH through Bay Trail, Avoton, Apollo Lake, Denverton, Gemini Lake, and related PCH families.

Important APIs, types, and functions: `lpc_chipset_info[]` maps enum chipsets to names, iTCO watchdog versions, GPIO versions, GPIO-info tables, and SPI types. `lpc_ich_priv` records config offsets and saved PCI config bytes. Static `mfd_cell`s represent `iTCO_wdt`, `gpio_ich`, and `intel-spi`; Apollo Lake and Denverton pinctrl cells use P2SB-derived MMIO resources. `lpc_ich_init_wdt()`, `lpc_ich_init_gpio()`, `lpc_ich_init_pinctrl()`, and `lpc_ich_init_spi()` discover resources and add children. `lpc_ich_restore_config_space()` restores ACPI/GPIO/PMC decode bits changed during probe.

Control flow: `lpc_ich_probe()` allocates private state, selects GPIO config offsets based on chipset generation, then independently attempts watchdog, legacy GPIO, pinctrl, and SPI initialization based on the chipset table. At least one child must register successfully. Each initializer reads PCI config or P2SB resources, validates ACPI/resource conflicts, enables decode where needed, fills resources/platform data, and calls `mfd_add_devices()`.

State and persistence: the driver temporarily changes PCI config decode bits for ACPI, GPIO, or PMC space and caches previous values for restore on remove or total probe failure. Child platform data includes watchdog version/name and GPIO capability data. Hardware BAR/decode state persists outside the driver unless restored.

Dependencies and integration points: PCI, ACPI conflict checks, MFD core, pinctrl, Intel P2SB helpers, iTCO watchdog platform data, intel-spi board info, software nodes, and downstream GPIO/pinctrl/SPI/watchdog drivers.

Risks: global static resource and cell objects are mutated (`num_resources`, starts/ends, platform data), so repeated bind/unbind and partial failures deserve scrutiny. Resource conflict handling intentionally ignores some conflicts and may register a reduced GPIO cell. SPI write-enable callbacks alter flash-protection bits. Tests should cover representative chipset entries for iTCO v1/v2/v3/v5, GPIO conflict paths, ACPI-present pinctrl skip, P2SB failures, SPI BYT/LPT/BXT resource discovery, config-space restore, and no-cell failure.
