# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/archrandom.h

Purpose: exposes PowerPC architecture random-number hooks to the generic kernel random subsystem.

Important APIs/types/functions: when `CONFIG_ARCH_RANDOM` is enabled it declares `powernv_get_random_long(unsigned long *v)`, `pseries_get_random_long(unsigned long *v)`, and `powerpc_arch_randomize_init(void)`.

Control flow: this header has no inline logic. Platform code implements the backend random retrieval functions, and random initialization code calls `powerpc_arch_randomize_init()` to wire the platform backend.

State and persistence: no state is stored here. Entropy state is owned by platform firmware/hardware and the generic random subsystem.

Dependencies and integration points: integrates PowerNV and pSeries firmware/hardware RNG providers with the generic `arch_get_random*` path under `CONFIG_ARCH_RANDOM`.

Risks: declarations are gated by config, so call sites must also be config-gated. Hardware or firmware RNG failures must be handled in implementation code by returning false rather than supplying weak values.

Test signals: build with `CONFIG_ARCH_RANDOM`, boot PowerNV and pSeries targets, verify random subsystem credits/uses arch randomness only on successful backend calls, and test failure paths on systems without RNG support.
