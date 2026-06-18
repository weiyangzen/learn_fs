# sources/distributed-fs/ceph-client/drivers/char/hw_random/arm_smccc_trng.c

## Purpose
This driver exposes the Arm SMCCC TRNG firmware interface as an hwrng provider. It reads entropy from firmware or a higher exception level using the SMCCC TRNG calls, abstracting machine-specific hardware access.

## Important APIs, Types, and Functions
- `ARM_SMCCC_TRNG_RND` selects 64-bit or 32-bit firmware calls by architecture.
- `copy_from_registers()` copies returned entropy from SMCCC result registers.
- `smccc_trng_read()` loops over firmware calls, handling success, no-entropy, invalid parameter, and other errors.
- `smccc_trng_probe()` allocates `struct hwrng` and registers it with name `smccc_trng`.

## Control Flow
Probe creates a platform-backed hwrng. Reads request up to three result registers per SMCCC call. On success, bytes are copied from registers into the caller buffer. On `NO_ENTROPY`, nonblocking callers receive what has already been copied, while blocking callers retry up to `SMCCC_TRNG_MAX_TRIES` with `cond_resched()`.

## State and Persistence Behavior
The driver has no persistent hardware state and no init/cleanup hooks. Runtime state is limited to stack counters during reads. Firmware owns entropy source state.

## Dependencies and Integration Points
It depends on `HAVE_ARM_SMCCC_DISCOVERY`, the platform device named `smccc_trng`, `linux/arm-smccc.h`, and hwrng core registration. The platform device is typically created by SMCCC discovery code.

## Risks
Trust and liveness are delegated to firmware. A broken firmware implementation can return repeated no-entropy or bad status, yielding short reads or `-EIO`. The driver bounds retries to avoid indefinite stalls.

## Test Signals
Use SMCCC discovery/emulation to test success sizes, 32-bit vs 64-bit register packing, no-entropy retry limit, nonblocking partial returns, unexpected firmware status errors, and module alias autoloading.
