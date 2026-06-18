# sources/distributed-fs/ceph-client/arch/mips/cobalt/Makefile

Purpose: selects the Cobalt board-support objects for the MIPS kernel build.

Important build behavior: `obj-y` always includes buttons, IRQ, LCD, LED, MTD, reset, RTC, serial, setup, and time support. `pci.o` is included only when `CONFIG_PCI` is enabled.

Dependencies and integration: this file ties Cobalt-specific source files into the architecture build; those files then register platform devices and board hooks.

Risks and test signals: missing an object here silently removes board functionality. Build tests should cover Cobalt with and without `CONFIG_PCI` to verify conditional inclusion.
