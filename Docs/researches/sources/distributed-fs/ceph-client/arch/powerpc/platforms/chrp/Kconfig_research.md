# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Kconfig

Purpose: declares the `PPC_CHRP` platform option for 32-bit Book3S Common Hardware Reference Platform machines.

Important configuration behavior: the option is a boolean prompt, depends on `PPC_BOOK3S_32`, defaults to enabled, and selects platform capabilities including PC speaker platform support, MPIC, i8259, indirect PCI, RTAS and RTAS daemon/error logging, MPC106, UDBG 16550, native hash MMU, and forced PCI.

Control flow and integration: selecting this option brings in the CHRP platform build subtree and its setup, PCI, time, NVRAM, and SMP support as controlled by the Makefile. It also constrains the platform to the legacy 32-bit PowerPC environment.

Risks and test signals: broad `select` usage can force dependencies on configurations that do not actually work for a board variant; default `y` affects multi-platform builds. Test signals are Kconfig dependency resolution, `oldconfig` behavior, and boot tests on CHRP/Pegasos/BriQ-like machines with expected interrupt, PCI, RTAS, and hash MMU support.
