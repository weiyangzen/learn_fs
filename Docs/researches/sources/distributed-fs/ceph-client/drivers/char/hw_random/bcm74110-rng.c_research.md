# sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm74110-rng.c

## Purpose
This driver exposes the Broadcom BCM74110 RNG FIFO to the hwrng core. It maps a simple host register block and reads available FIFO words with a bounded wait when blocking.

## Important APIs, Types, and Functions
- `struct bcm74110_priv` stores MMIO base.
- `bcm74110_rng_fifo_count()` reads and masks `HOST_FIFO_COUNT`.
- `bcm74110_rng_read()` waits briefly for FIFO data and drains up to `max`.
- `bcm74110_rng_probe()` maps resources, fills static hwrng name/private pointer, and registers.

## Control Flow
Probe maps the OF-described MMIO region and registers a static hwrng object. Reads loop while FIFO count is zero, returning immediately for nonblocking callers or after a small bounded retry budget for blocking callers. Once words are available, the driver reads until requested capacity or FIFO underrun.

## State and Persistence Behavior
State is minimal: a private MMIO pointer stored through the hwrng `priv` field. There is no explicit enable, reset, or cleanup sequence. FIFO state is hardware-owned.

## Dependencies and Integration Points
It depends on OF compatible `brcm,bcm74110-rng`, platform MMIO, hwrng core, and relaxed MMIO reads.

## Risks
The static `bcm74110_hwrng` object makes multiple instances unsafe because name and priv are overwritten. Blocking waits are intentionally short and may return zero even if entropy appears later.

## Test Signals
Test no-MMIO probe failure, FIFO empty blocking/nonblocking reads, FIFO underrun during drain, multiple device instances, and `/dev/hwrng` throughput under repeated reads.
