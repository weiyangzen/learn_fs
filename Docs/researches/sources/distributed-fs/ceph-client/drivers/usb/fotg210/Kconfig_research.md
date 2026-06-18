# sources/distributed-fs/ceph-client/drivers/usb/fotg210/Kconfig

Purpose: declares configuration options for the Faraday FOTG210 USB2 dual-role controller and its host/peripheral subdrivers.

Important APIs/functions: config symbols are `USB_FOTG210`, `USB_FOTG210_HCD`, and `USB_FOTG210_UDC`. The top-level option is tristate, depends on USB or USB_GADGET, DMA, IOMEM, and Gemini architecture or compile-test, defaults on Gemini, and selects `MFD_SYSCON`.

Control flow: when `USB_FOTG210` is enabled, users can select host controller support if USB linkage is compatible or peripheral support if USB gadget linkage is compatible. Help text explains module names and current peripheral bulk-transfer scope.

State and persistence: build-time configuration only. It determines which driver code is compiled and linked.

Dependencies and integration: integrates with Linux USB host and gadget Kconfig, architecture selection, compile testing, DMA/IOMEM availability, and Gemini syscon support needed by the core platform driver.

Risks: dependency expressions around built-in vs module linkage are important; invalid combinations could produce unresolved symbols or missing role support. The top-level dual-role controller does not imply dynamic role switching; actual mode is selected by device tree/dr_mode and core probing.

Test signals: `allmodconfig`/`allyesconfig`/`COMPILE_TEST`, Gemini defconfig, module builds for host and UDC, and boot tests in host and peripheral modes.
