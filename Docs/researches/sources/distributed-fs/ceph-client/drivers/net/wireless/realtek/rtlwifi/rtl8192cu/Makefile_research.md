
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/Makefile

Purpose: Builds the `rtl8192cu` USB driver module from its per-device implementation objects and connects it to `CONFIG_RTL8192CU`.

Important APIs/types/functions: The object list is `dm.o`, `hw.o`, `led.o`, `mac.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8192CU) += rtl8192cu.o` binds the composite object to the kernel Kconfig symbol.

Control flow: No runtime control flow. At build time, Kbuild combines the listed objects into `rtl8192cu.o`; `sw.o` provides module/USB driver registration, while other objects provide HAL operations referenced from the configuration tables.

State and persistence: Build artifact only. The ordering matters only for link visibility and reproducibility, not runtime initialization order.

Dependencies/integration: The module relies on shared rtlwifi infrastructure and shared 8192C/8192CE headers included from the C files. Omitting any object breaks HAL op resolution, firmware/table access, or USB TRX behavior.

Risks: Since `mac.o` contains functions also used by PCIe-family code concepts, moving it can affect symbol ownership. Kconfig-disabled builds should not compile this module. New source files require explicit addition here.

Test signals: `make M=drivers/net/wireless/realtek/rtlwifi/rtl8192cu` or an equivalent subtree build should produce one module with no unresolved symbols. Modpost should include firmware declarations from `sw.o`.
