# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Makefile

Purpose: builds `board-artpec6.o` when `CONFIG_MACH_ARTPEC6` is enabled.

Control flow is build-time only. Dependencies are the ARTPEC6 Kconfig symbol and the machine descriptor in `board-artpec6.c`. Risks are missing board object causing DT machine match failure. Test signals are successful ARTPEC6 links and machine descriptor presence in vmlinux.
