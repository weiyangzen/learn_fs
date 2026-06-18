# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rng.c

Purpose: Installs pSeries firmware random seed support via the `H_RANDOM` hypercall when an `ibm,random` device-tree node exists.

Important APIs/types/functions: Implements `pseries_get_random_long()` and `pseries_rng_init()`.

Control flow: Init searches for compatible node `ibm,random`; if present, it assigns `ppc_md.get_random_seed`. Calls to that hook invoke `H_RANDOM`, return the first hypercall result word on success, and report failure otherwise.

State and persistence: Only mutates the machine descriptor hook. Random values are not cached.

Dependencies and integration points: Depends on OF compatible nodes, PAPR hcall wrappers, arch random seed plumbing, and pseries setup calling `pseries_rng_init()`.

Risks: Availability is inferred from device tree, not from probing the hcall at init. Runtime hcall failures simply return no seed.

Test signals: Boot with and without `ibm,random`, successful and failing `H_RANDOM`, random seed consumers, and OF node reference cleanup.

Source read size: 37 lines, 818 bytes.
