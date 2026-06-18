<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c

Purpose: Provides Tundra TSI108/109 bridge common device setup, especially CSR base discovery and Ethernet platform-device creation from OF nodes.

Important APIs/types/functions: Exports `get_csrbase()` and `get_vir_csrbase()`. Initcall `tsi108_eth_of_init()` creates `tsi-ethernet` platform devices and fills `hw_info`.

Control flow: CSR helpers lazily find the `tsi-bridge` resource and map CSR space. Ethernet init scans `network` nodes compatible with `tsi108-ethernet`, translates MAC resources/IRQs, registers a platform device, extracts MAC address, MDIO and PHY phandles/resources, PHY id, IRQ number, and optional `txc-rxc-delay-disable` workaround flag, then attaches platform data.

State and persistence: Persistent state is cached physical CSR base, mappings returned by `get_vir_csrbase()`, and registered Ethernet platform devices with copied hardware info.

Dependencies and integration points: Depends on OF address/IRQ/net helpers, TSI108 register definitions, platform bus, legacy `tsi-ethernet` driver, and PHY/MDIO phandles.

Risks: `get_vir_csrbase()` maps CSR space on every call and returns a truncated `u32` virtual address. Ethernet registration passes only one resource even though it constructs an IRQ resource separately, relying on platform data for IRQ. Missing `mdio-handle`/`phy-handle` properties are not defensively checked before dereference.

Test signals: TSI108 board boot, Ethernet platform device creation, MAC/PHY/MDIO property parsing, workaround property behavior, and leak/error-path testing for missing phandles.

Source read size: 153 lines, 3596 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c -->
