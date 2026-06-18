# sources/distributed-fs/ceph-client/drivers/char/hw_random/ixp4xx-rng.c

## Purpose
This small driver exposes the Intel IXP45x/46x NPU pseudo-random generator through hwrng. It maps the RNG register and returns one raw 32-bit value per read.

## Important APIs, Types, and Functions
- `ixp4xx_rng_data_read()` reads a 32-bit value from the mapped base address.
- Static `ixp4xx_rng_ops` registers the legacy `data_read` callback.
- `ixp4xx_rng_probe()` verifies `cpu_is_ixp46x()`, maps MMIO, stores the base in `priv`, and registers devm hwrng.

## Control Flow
Platform probe rejects non-IXP46x CPUs, maps the resource, and registers the hwrng. The core treats data as always present because only `data_read` is supplied. Each read returns four bytes.

## State and Persistence Behavior
State is a static hwrng object with one `priv` MMIO pointer. There is no enable, cleanup, or software buffer.

## Dependencies and Integration Points
It depends on OF compatible `intel,ixp46x-rng`, IXP4xx CPU detection helpers, platform MMIO, and hwrng core.

## Risks
The static hwrng object is not multi-instance safe. The generator is pseudo-random and has no readiness or health check in this driver. Probe is gated by CPU family even if devicetree matches.

## Test Signals
Test CPU family rejection, MMIO mapping failure, one-word reads, devm unregister, and static-object behavior if multiple platform devices are described.
