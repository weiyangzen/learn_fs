# sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm2835-rng.c

## Purpose
This platform driver supports Broadcom BCM2835/BCM63xx/NSP-style RNG blocks. It handles optional clock and reset resources, optional interrupt masking for some variants, warm-up discard count programming, and FIFO-based word reads.

## Important APIs, Types, and Functions
- `struct bcm2835_rng_priv` stores hwrng, MMIO base, variant interrupt-mask flag, optional clock, and optional reset.
- `bcm2835_rng_init()` enables the clock, resets hardware, masks interrupts if needed, writes warm-up count, and enables generation.
- `bcm2835_rng_read()` waits for FIFO count in `RNG_STATUS[31:24]` and reads up to caller capacity.
- Endian-aware `rng_readl()`/`rng_writel()` use raw MMIO on big-endian MIPS variants.

## Control Flow
Probe maps the peripheral, obtains optional clock/reset, records OF variant data, sets hwrng callbacks, and registers. Core init powers the RNG and starts generation. Reads spin/yield while no words are available if blocking, then drain the available FIFO words. Cleanup disables generation and clock.

## State and Persistence Behavior
Hardware enable, warm-up count, interrupt mask, clock, and reset state persist while the hwrng is selected. No software buffer is maintained.

## Dependencies and Integration Points
It supports multiple OF compatibles and platform IDs, integrates with reset and clock frameworks, hwrng core, and architecture endian configuration.

## Risks
Blocking reads can yield repeatedly without an explicit timeout. Endian-specific raw access is necessary for BMIPS-like systems; changing it can break those variants. Warm-up count assumes hardware discards weaker early values.

## Test Signals
Test each compatible/ID, optional clock and reset absence, interrupt mask variants, big-endian MIPS accessors, FIFO empty nonblocking reads, and repeated init/cleanup through sysfs hwrng selection.
