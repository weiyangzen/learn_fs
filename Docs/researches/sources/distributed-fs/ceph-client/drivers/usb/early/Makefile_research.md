# sources/distributed-fs/ceph-client/drivers/usb/early/Makefile

Purpose: wires early USB debug console objects into the kernel build based on Kconfig selections.

Important APIs/functions: no C API. Build targets are `ehci-dbgp.o` for `CONFIG_EARLY_PRINTK_DBGP` and `xhci-dbc.o` for `CONFIG_EARLY_PRINTK_USB_XDBC`.

Control flow: kbuild conditionally adds the corresponding object files to `obj-y`/`obj-m` style build lists according to config symbols.

State and persistence: none at runtime; it controls which early-console implementations are linked into the kernel.

Dependencies and integration: depends on Kconfig symbols defined elsewhere for early printk over EHCI debug port and xHCI debug capability. It sits under USB early drivers and feeds the top-level kernel build.

Risks: incorrect config symbols would silently exclude early console support. Building these objects in unsupported architectures/configurations can fail because the C files depend on early PCI, fixmap, and low-level x86-style direct PCI access.

Test signals: build with each config enabled, confirm the expected object is compiled, and boot with `earlyprintk=dbgp` or xDBC parameters to verify linked code is available.
