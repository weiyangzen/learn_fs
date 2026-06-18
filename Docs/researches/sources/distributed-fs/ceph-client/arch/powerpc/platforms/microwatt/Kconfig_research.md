# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Kconfig

Purpose: Kconfig symbol for FPGA-based Microwatt SoC support.

Important APIs and control flow: `PPC_MICROWATT` depends on 64-bit Book3S PowerPC and selects XICS native interrupt support, 16550 udbg, and common clock support. The help text identifies FPGA Microwatt implementations.

State, dependencies, and risks: state is compile-time selection. Dependencies control whether `setup.o`, `rng.o`, and optional SMP support can use XICS and DARN assumptions. Risks are under-specified platform dependencies for evolving Microwatt firmware/device trees. Test signals are defconfig selection, successful link with XICS/native ICP/ICS, and boot on a Microwatt SoC DT.
