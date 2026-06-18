# sources/distributed-fs/ceph-client/drivers/char/hw_random/ks-sa-rng.c

## Purpose
This driver exposes the TI Keystone NETCP Security Accelerator TRNG. It enables the SA module through syscon, configures TRNG sampling/refill cycles, tracks expected readiness timestamps, and returns 64-bit output through legacy hwrng callbacks.

## Important APIs, Types, and Functions
- `struct trng_regs` maps output, status, interrupt, control, and config registers.
- `struct ks_sa_rng` stores hwrng, clock, syscon regmap, MMIO registers, readiness timestamp, and refill delay.
- `cycles_to_ns()`, `startup_delay_ns()`, and `refill_delay_ns()` derive timing from clock rate.
- `ks_sa_rng_init()` enables/configures hardware and computes delays.
- `ks_sa_rng_data_present()` waits until expected ready time and polls status.
- `ks_sa_rng_data_read()` reads low/high output, acknowledges ready, and updates next ready time.

## Control Flow
Probe maps TRNG registers, obtains the syscon regmap and clock, enables runtime PM/power domain, and registers hwrng. Core init enables SA TRNG and programs timing. The hwrng core first calls `data_present`; when ready, `data_read` returns two words and acknowledges the interrupt/status.

## State and Persistence Behavior
`ready_ts` and `refill_delay_ns` persist across reads to avoid polling before hardware can refill. Hardware enable/config registers persist until cleanup. Runtime PM is enabled at probe and released on remove.

## Dependencies and Integration Points
It depends on OF compatible `ti,keystone-rng`, `ti,syscon-sa-cfg` phandle, regmap, platform MMIO, clocks, runtime PM, and hwrng core.

## Risks
Timing constants are hard-coded defaults, so hardware characterization changes require code updates. The remove path only handles PM; hwrng cleanup disables hardware when the core unregisters. `data_present` truncates nanosecond delta to `u32` for sleep calculation.

## Test Signals
Test missing syscon/clock/MMIO, startup and refill delays at different clock rates, status-ready polling, output ack, runtime PM enable/disable, and repeated reads under high demand.
