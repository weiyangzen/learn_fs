# sources/distributed-fs/ceph-client/drivers/char/hw_random/cn10k-rng.c

## Purpose
This PCI driver exposes Marvell CN10K RVU RNG hardware through hwrng. It maps PF registers, checks entropy block health, optionally uses extended TRNG registers on newer revisions, and falls back to legacy random registers with zero-value mitigation.

## Important APIs, Types, and Functions
- `struct cn10k_rng` stores register base, hwrng ops, PCI device, and extended-register support flag.
- `cn10k_is_extended_trng_regs_supported()` gates extended TRNG use based on subsystem device and revision.
- `reset_rng_health_state()` issues an SMC call to reset EBG health state.
- `check_rng_health()` checks `RNM_PF_EBG_HEALTH` and resets health state when failure is detected.
- `cn10k_read_trng()` reads extended or legacy random data.
- `cn10k_rng_read()` fills caller buffers in 64-bit and trailing-byte chunks.

## Control Flow
Probe maps BAR0, names and registers the hwrng, determines revision capability, and resets health state. Reads first check health. Extended-register reads try `RNM_PF_TRNG_DAT` and status. Legacy reads use `RNM_PF_RANDOM`; if zero appears, the driver combines nonzero upper/lower halves from subsequent reads.

## State and Persistence Behavior
Driver state is per PCI device and devm-managed. Hardware health state can be reset through secure firmware. Extended-register capability is fixed at probe.

## Dependencies and Integration Points
It depends on PCI vendor `CAVIUM` device `0xA098`, MMIO, Arm SMCCC SMC services, hwrng core, and CN10K firmware support for the health reset call.

## Risks
Legacy zero mitigation can busy-loop until nonzero halves appear. Health reset failure returns `-EIO`, disabling reads. Revision filtering must stay aligned with errata for extended TRNG register availability.

## Test Signals
Test supported and unsupported revisions, SMC health reset success/failure, extended register no-status timeout, legacy zero handling, arbitrary read sizes, and PCI probe failure cleanup.
