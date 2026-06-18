
# sources/distributed-fs/ceph-client/drivers/cxl/Makefile

Purpose: top-level Kbuild orchestration for CXL driver objects and modules.

Important APIs, types, and functions: always descends into `core/`, then builds `cxl_port.o`, `cxl_acpi.o`, `cxl_pmem.o`, `cxl_mem.o`, and `cxl_pci.o` according to config. Object aliases map modules to `port.o`, `acpi.o`, `pmem.o security.o`, `mem.o`, and `pci.o`.

Control flow: no runtime logic, but comments document built-in link order constraints: core first, port before platform root drivers, mem/pmem before endpoint drivers, and PCI last to mirror hardware enumeration.

State and persistence: no runtime state.

Dependencies and integration points: integrates with Kbuild and Kconfig symbols from `drivers/cxl/Kconfig`. Link order affects CXL bus availability during early platform and PCI discovery.

Risks and test signals: reordering can break built-in boot discovery, especially ACPI root ports and endpoint attach timing. Test signals include built-in boot with ACPI CEDT, modular load ordering, softdeps, and immediate memdev/port enumeration.
