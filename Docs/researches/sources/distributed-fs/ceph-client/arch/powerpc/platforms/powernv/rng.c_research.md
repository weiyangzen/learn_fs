## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/rng.c

### Purpose
`rng.c` wires PowerNV random-number sources into `ppc_md.get_random_seed`, preferring POWER9 DARN and falling back to device-tree `ibm,power-rng` MMIO engines.

### Important APIs, Types, And Functions
`struct pnv_rng` holds virtual and real-mode MMIO addresses plus a whitening mask. Key functions are `initialise_darn()`, `pnv_get_random_darn()`, exported `pnv_get_random_long()`, `rng_create()`, `pnv_get_random_long_early()`, `pnv_rng_init()`, and `pnv_rng_late_init()`.

### Control Flow
Early platform setup calls `pnv_rng_init()`. DARN is tested up to ten times on ARCH_300 CPUs and installed if usable. Otherwise, an early lazy callback waits until slab allocation works, creates `pnv_rng` objects for `ibm,power-rng` nodes, maps registers, assigns each CPU to the same-chip RNG where possible, and replaces the callback with `pnv_get_random_long()`. The late init path forces lazy setup if needed and publishes OF platform devices.

### State, Persistence, And Dependencies
State is per-CPU RNG pointer assignment plus the mutable per-device whitening mask. Reads use normal MMIO when translation is on and real-mode reads when MSR_DR is off. Dependencies include OF address parsing, chip-id topology, `asm/archrandom.h`, DARN opcodes, and PowerNV machine init calls.

### Integration Points
The file feeds architecture random seed consumers through `ppc_md.get_random_seed` and exports `pnv_get_random_long()` for GPL users.

### Risks
The fallback assumes every CPU gets a non-NULL RNG pointer before use. The whitening mask is updated without locking and may be shared by CPUs on the same chip. DARN error handling must reject the all-ones failure value.

### Test Signals
Boot logs on POWER8/POWER9, `ibm,power-rng` DT coverage, early and late random seed calls, real-mode callers, and repeated DARN failure injection are useful signals.
