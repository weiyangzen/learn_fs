<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile

Purpose: Kbuild object mapping for Xillybus drivers.

Important APIs/types/functions: Maps `CONFIG_XILLYBUS_CLASS` to `xillybus_class.o`, `CONFIG_XILLYBUS` to `xillybus_core.o`, `CONFIG_XILLYBUS_PCIE` to `xillybus_pcie.o`, `CONFIG_XILLYBUS_OF` to `xillybus_of.o`, and `CONFIG_XILLYUSB` to `xillyusb.o`.

Control flow: no runtime flow.

State and persistence: no runtime state.

Dependencies and integration: implements the module split described by Kconfig: shared class, shared PCIe/OF core, transport wrappers, and independent USB driver.

Risks: transport modules depend on symbols exported by class/core according to Kconfig selections; Makefile/Kconfig drift can produce unresolved symbols.

Test signals: compile all Kconfig combinations, inspect module dependencies, and modprobe PCIe/OF/USB variants with `xillybus_class` available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Makefile -->
