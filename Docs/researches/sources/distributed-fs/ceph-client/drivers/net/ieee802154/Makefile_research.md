# sources/distributed-fs/ceph-client/drivers/net/ieee802154/Makefile

Purpose: Maps IEEE 802.15.4 Kconfig symbols to the object files compiled for each driver in this directory.

Important APIs, types, and symbols: Standard kernel build variables `obj-$(CONFIG_...) += ...` include `fakelb.o`, `at86rf230.o`, `mrf24j40.o`, `cc2520.o`, `atusb.o`, `adf7242.o`, `ca8210.o`, `mcr20a.o`, and `mac802154_hwsim.o` based on configuration.

Control flow: During kbuild, each enabled symbol contributes the corresponding object as built-in or module according to the symbol value. Module names follow object basenames unless additional composite object rules are added elsewhere.

State and persistence behavior: This file has no runtime state. Its output is build artifacts and modules determined by `.config`.

Dependencies and integration points: It must stay synchronized with `Kconfig` symbols and source filenames in `drivers/net/ieee802154`. It integrates with the Linux kernel recursive make system.

Risks and edge cases: A mismatch between Kconfig symbol, source filename, or Makefile object entry silently prevents an enabled driver from building or causes build errors. Composite drivers would require additional `foo-y` rules not present here.

Test signals: Build each `CONFIG_IEEE802154_*` option as module and built-in, and run `make M=drivers/net/ieee802154` or equivalent subtree builds to verify object mapping.
