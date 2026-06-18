# sources/distributed-fs/ceph-client/drivers/pci/Makefile

Purpose: object list for the PCI core, feature modules, and subdirectories. It wires Kconfig symbols into compilation units and ensures endpoint/controller/switch directories are traversed.

Important build rules: `obj-$(CONFIG_PCI)` builds core files including `access.o`, `bus.o`, `probe.o`, `pci.o`, resource setup, IRQ, VPD, driver, and mmap/devres support. Conditional additions cover procfs, sysfs, ACPI, iomap, OF, quirks, ATS, IOV, ECAM, P2PDMA, Xen, VGA arbiter, DOE, IDE, TSM, NPEM, TPH, and CardBus setup. `obj-y` always enters `controller/` and `switch/`, while endpoint is ordered before users.

Control flow/state: no runtime state, but build order matters for endpoint initialization and subdirectory inclusion. `subdir-ccflags-$(CONFIG_PCI_DEBUG)` adds `-DDEBUG`; `trace.o` gets an include path and is built with tracing.

Dependencies/integration: consumes symbols from the top PCI Kconfig and exposes subdirectory builds to controller Kconfigs. Risks include missing objects for selected symbols, ordering regressions, and always-descending directories relying on internal Kconfig guards. Test signals are `make drivers/pci/`, allyesconfig/allmodconfig object coverage, and absence of missing-symbol link errors.
