# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/Makefile

Purpose: kbuild composition for Marvell Octeon endpoint vDPA.

Important APIs/types/functions: `obj-$(CONFIG_OCTEONEP_VDPA) += octep_vdpa.o`; composite object includes `octep_vdpa_main.o` and `octep_vdpa_hw.o`.

Control flow: builds Octeon vDPA only when the module-only Kconfig symbol is enabled.

State and persistence: build-only file.

Dependencies and integration: reached from top-level vDPA Makefile; Kconfig requires PCI MSI and module build.

Risks: adding implementation files requires updating the composite list. Kconfig notes the module cannot be loaded until Octeon emulation software is running.

Test signals: module build with `CONFIG_OCTEONEP_VDPA=m` and link coverage for main/hardware objects.
