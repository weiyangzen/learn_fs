<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile

Purpose: maps 44x Kconfig symbols to the platform object files that implement common SoC setup, board descriptors, PCI/MSI support, power management, GPIO, and interrupt handling.

Important APIs/types/functions: always builds `misc_44x.o`, `machine_check.o`, `uic.o`, and `soc.o`; builds `idle.o` unless CPM is selected; conditionally builds `ppc44x_simple.o`, board files, `pci.o`, `hsta_msi.o`, `cpm.o`, and `gpio.o`.

Control flow: make evaluates Kconfig-driven `obj-*` assignments at build time. The resulting object list determines which `define_machine()`, initcall, and driver registration code enters the kernel.

State and persistence: build-time only.

Dependencies and integration: tied to symbols in `Kconfig`, generic powerpc platform linking, and initcall ordering inside each object.

Risks and test signals: missing object entries can make a selected board unbootable; unconditional common objects must remain safe across all 44x variants. Test per-board builds and confirm no duplicate machine descriptors conflict for enabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile -->
