# sources/distributed-fs/ceph-client/drivers/char/hw_random/hisi-rng.c

## Purpose
This driver supports HiSilicon Hip04/Hip05 RNG hardware. It seeds the generator from kernel randomness, optionally selects ring-oscillator seed reload, enables generation, and returns one 32-bit random number per read.

## Important APIs, Types, and Functions
- `seed_sel` module parameter selects LFSR or ring-oscillator seed reload.
- `struct hisi_rng` stores MMIO base and hwrng.
- `hisi_rng_init()` writes `RNG_SEED` and enables `RNG_CTRL` bits.
- `hisi_rng_cleanup()` disables the RNG.
- `hisi_rng_read()` reads `RNG_RAN_NUM`.

## Control Flow
Probe maps MMIO, fills callbacks, and registers devm hwrng. Core init seeds and enables the hardware. Reads directly return one word. Cleanup clears control bits.

## State and Persistence Behavior
The selected seed mode is global module state. Hardware seed and control bits persist while selected. There is no readiness polling or software buffer.

## Dependencies and Integration Points
It depends on OF compatibles `hisilicon,hip04-rng` and `hisilicon,hip05-rng`, platform MMIO, hwrng core, and `get_random_bytes()` for initial seed.

## Risks
Reads do not check readiness or health status, so correctness depends on hardware always having valid output after enable. The module parameter is global across possible instances.

## Test Signals
Test both compatibles, seed parameter modes, init/cleanup register writes, repeated reads, and probe resource failures.
