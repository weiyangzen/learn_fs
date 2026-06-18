# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/Makefile

Purpose: build composition for SGI IP22/IP28 platform support. It always includes memory-controller, HPC, interrupt, timer, NVRAM, platform-device, reset, setup, and GIO bus code, with bus-error and EISA objects selected by config.

Important APIs and control flow: `obj-y` includes the core IP22 objects. `ip22-berr.o` is selected for `CONFIG_SGI_IP22`, `ip28-berr.o` for `CONFIG_SGI_IP28`, and `ip22-eisa.o` for `CONFIG_EISA`.

State, persistence, and integration: no runtime state is created by the Makefile, but it determines which `ip22_be_init()` implementation is linked. Dependencies include mutually appropriate SGI IP22/IP28 Kconfig choices. Risks include wrong bus-error handler for a machine variant and optional EISA code only present under config. Test signals are expected object inclusion and successful link for Indy, Indigo2, and IP28 builds.
