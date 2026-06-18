# sources/distributed-fs/ceph-client/drivers/virt/acrn/Makefile

Purpose: Makefile for the ACRN HSM driver aggregate object.

Important APIs, types, and functions: `obj-$(CONFIG_ACRN_HSM) := acrn.o`; `acrn-y` links `hsm.o`, `vm.o`, `mm.o`, `ioreq.o`, `ioeventfd.o`, and `irqfd.o` into the driver.

Control flow: Kbuild creates one `acrn` module/built-in object from the listed compilation units when `CONFIG_ACRN_HSM` is enabled.

State and persistence: build-system only.

Dependencies and integration points: ties the files researched here (`hsm.c`, `ioeventfd.c`, headers) to companion VM/memory/ioreq/irqfd implementation files outside this work item.

Risks: the driver is incomplete if any listed object does not compile; interface contracts in `acrn_drv.h` span all components.

Test signals: module and built-in link tests for `CONFIG_ACRN_HSM`; symbol resolution across all six objects.
