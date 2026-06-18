# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2rng.h

Purpose: shared Niagara2 RNG definitions for the C driver and related assembly hypervisor call stubs.

Important APIs, types, and functions: defines v1/v2 control bitfields, hypervisor function numbers, HV RNG states, `enum n2rng_compat_id`, `struct n2rng_template`, `struct n2rng_unit`, and `struct n2rng`. It declares `sun4v_rng_get_diag_ctl()`, control read/write helpers, diagnostic data reads, and normal data reads.

Control flow: this header has no executable flow, but it defines the contract used by `n2-drv.c`: control register layout differs by chip generation, HV API v1 lacks per-unit arguments while v2 includes units/watchdog status, and shared state values move hardware between unconfigured, configured, healthcheck, and error states.

State and persistence: all persistent runtime state is represented in `struct n2rng`: flags, unit count/control words, hwrng object, cached `u32` buffer, HV API version, delayed work, health parameters, scratch/test buffers, and test controls.

Dependencies and integration: included by `n2-drv.c` and assembly code; requires Linux types and hwrng/platform declarations on the C side and avoids C declarations under `__ASSEMBLER__`.

Risks and test signals: bitfield drift would silently misprogram entropy sources. Tests should verify compile coverage for assembly/C users, chip-version-specific control masks, struct field assumptions used by the driver, and limits such as `N2RNG_BLOCK_LIMIT`, `N2RNG_BUSY_LIMIT`, and self-test constants.
