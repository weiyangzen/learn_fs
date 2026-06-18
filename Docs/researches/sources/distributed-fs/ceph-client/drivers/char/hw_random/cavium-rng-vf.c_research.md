# sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng-vf.c

## Purpose
This PCI VF driver exposes Cavium ThunderX/OcteonTx RNG output through hwrng. It maps the VF result BAR, optionally maps PF health registers, checks health status before reads, and reads arbitrary byte counts from the result register.

## Important APIs, Types, and Functions
- `struct cavium_rng` stores hwrng ops, result MMIO, optional PF CSR base, PCI device, clock rate, and previous health-error timing.
- `cavium_rng_read()` calls `check_rng_health()` and reads 64-bit or byte chunks.
- `cavium_map_pf_regs()` locates/maps the PF device for health status unless running on older OcteonTx CPUs.
- `check_rng_health()` detects startup and persistent health failures using PF status and architectural timer deltas.
- `cavium_rng_probe_vf()` maps BAR0, names the hwrng, maps PF registers, and registers.

## Control Flow
VF probe allocates state, maps the result BAR, sets a device-unique hwrng name, maps PF CSRs for health checking when supported, and registers. Each read first validates health. If healthy, the read path streams as many 64-bit values as possible and handles trailing bytes from byte reads.

## State and Persistence Behavior
Per-device state is devm-managed except the PF mapping is manually unmapped on remove. `prev_error` and `prev_time` persist across reads to decide whether health failures are new/persistent. The PF driver separately enables the RNG and SR-IOV VF.

## Dependencies and Integration Points
It depends on PCI vendor/device IDs, hwrng core, ARM64 MIDR helpers, arch timer reads, and a paired Cavium RNG PF device for enabling hardware and health registers.

## Risks
The remove path unconditionally `iounmap()`s `pf_regbase`, which can be `NULL` on OcteonTx. Health timing assumes CNTVCT runs at 100 MHz in a comment, making portability sensitive. Read ignores `wait` because the register interface is always sampled directly.

## Test Signals
Test VF probe with/without PF present, older CPU model health-skip path, startup health failure, repeated health failure timing, arbitrary read sizes, and remove with `pf_regbase == NULL`.
