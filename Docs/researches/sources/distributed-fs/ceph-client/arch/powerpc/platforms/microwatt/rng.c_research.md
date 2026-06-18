# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/rng.c

Purpose: Microwatt random-seed provider using the Power ISA DARN instruction.

Important APIs and control flow: `microwatt_get_random_darn` executes `PPC_DARN` with `L=1` for a 64-bit conditioned random value, treats all-ones as failure, and returns success/failure. `microwatt_rng_init` tries up to ten reads and installs `ppc_md.get_random_seed` on the first successful result.

State, dependencies, and risks: state is the machine callback `ppc_md.get_random_seed`; no persistent device state is kept. Dependencies include DARN instruction support, archrandom macros, and Microwatt setup ordering. Risks are CPU/FPGA implementations without a functioning DARN source, no logging on failure, and reliance on all-ones as the only error sentinel. Test signals are boot-time callback installation, entropy reads not returning DARN_ERR, and no illegal-instruction fault on Microwatt builds.
