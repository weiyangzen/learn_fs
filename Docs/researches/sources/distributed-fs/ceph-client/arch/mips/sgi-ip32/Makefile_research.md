# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/Makefile

Purpose: build composition for SGI IP32/O2 platform support. It includes bus-error, interrupt, platform-device, setup, reset, CRIME, memory, and DMA translation code.

Important APIs and control flow: `obj-y` adds `ip32-berr.o ip32-irq.o ip32-platform.o ip32-setup.o ip32-reset.o crime.o ip32-memory.o ip32-dma.o`.

State, persistence, and integration: no runtime state is created, but this ensures CRIME/MACE globals, DMA translation, platform devices, and machine hooks are linked. Dependencies include SGI IP32 config. Risks are link-time platform completeness only, with no optional object guards here. Test signals are successful IP32 kernel link and presence of CRIME/MACE setup symbols.
