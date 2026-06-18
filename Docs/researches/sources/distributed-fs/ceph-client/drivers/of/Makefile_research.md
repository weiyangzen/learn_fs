# sources/distributed-fs/ceph-client/drivers/of/Makefile

Purpose: Object list controlling which OF infrastructure components build for each Kconfig symbol.

Important APIs/types/functions: always builds `base.o cpu.o device.o module.o platform.o property.o`; conditionally includes `kobj.o`, `dynamic.o`, `fdt.o`, `fdt_address.o`, `pdt.o`, `address.o`, `irq.o`, `unittest.o`, reserved memory, resolver, overlay, NUMA, kexec, KUnit helpers/tests, overlay tests, and unittest data.

Control flow: kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` entries after Kconfig resolution. Nested `CONFIG_KEXEC_FILE` and `CONFIG_OF_FLATTREE` add `kexec.o` only when both are enabled.

State/persistence: no runtime state; determines compiled artifacts and link order.

Dependencies/integration: directly aligned with `drivers/of/Kconfig`. Overlay KUnit test builds a composite `overlay-test-y` from code and DTBO object.

Risks: missing or mismatched Kconfig guards would produce unresolved symbols or omit required OF helpers. Link order matters for built-in initialization and test data availability.

Test signals: build all relevant Kconfig combinations, especially OF address without PCI, overlay KUnit, KEXEC_FILE+FLATTREE, and OF_UNITTEST data inclusion.
