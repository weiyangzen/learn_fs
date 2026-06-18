# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Makefile

Purpose: object list for Microwatt platform support.

Important APIs and control flow: always builds `setup.o` and `rng.o`; builds `smp.o` only with `CONFIG_SMP`.

State, dependencies, and risks: state is build-time object inclusion. Dependencies are the `PPC_MICROWATT` Kconfig symbol and optional SMP. Risks are missing SMP release logic when SMP is enabled without `smp.o`, or dead code if RNG support is built for a CPU without usable DARN. Test signals are compile/link coverage for SMP and non-SMP Microwatt builds.
