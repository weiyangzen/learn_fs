# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/microwatt.h

Purpose: local Microwatt declarations shared between setup, RNG, and SMP code.

Important APIs and control flow: declares `microwatt_rng_init` and `microwatt_init_smp`; no inline logic is present.

State, dependencies, and risks: state is external to the header. Dependencies are object inclusion by Makefile and `__init` call ordering from `setup.c`. Risks are link failures if declarations and Kconfig object selection drift. Test signals are build coverage for Microwatt SMP and non-SMP configurations.
