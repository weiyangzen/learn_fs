# sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.c

## Purpose
This platform driver supports Arm CryptoCell 703/713 TRNG hardware. It configures ring oscillator sampling ratios from devicetree, collects entropy holding register data via IRQ and workqueues, buffers generated words in a circular buffer, handles runtime PM, and registers an hwrng provider with full entropy quality.

## Important APIs, Types, and Functions
- `struct cctrng_drvdata` stores platform device, MMIO base, clock, hwrng, active ROSC, sampling ratios, circular buffer, work items, pending flag, and read lock.
- `cc_trng_parse_sampling_ratio()` reads `arm,rosc-ratio`.
- `cc_trng_hw_trigger()` programs sampling, reset, debug, config, watchdog, and source enable registers.
- `cctrng_read()` copies from the circular buffer and schedules hardware refill work.
- `cc_isr()` masks RNG interrupts and schedules completion work.
- `cc_trng_compwork_handler()` validates ISR status, handles FIPS CRNGT failures, copies EHR words, changes ROSC on autocorrelation/watchdog errors, and releases PM usage.
- `cctrng_suspend()`/`cctrng_resume()` manage power-down and reset completion.

## Control Flow
Probe validates buffer constraints, allocates state, maps registers, gets IRQ and clock, initializes work and PM, takes an initial runtime PM reference, registers hwrng, and triggers the first hardware collection. The IRQ clears host causes and schedules deferred work. Completion work reads the RNG ISR, handles errors, copies six EHR words into the ring, and either starts another collection or autosuspends. Reads take a spin trylock, copy available buffered words, and schedule collection if buffer space permits.

## State and Persistence Behavior
The circular buffer persists entropy between IRQ completions and user/core reads. `pending_hw` prevents concurrent hardware operations. Runtime PM state and clock enablement persist around pending collection windows. Active ROSC advances on health-related collection errors. In FIPS mode, CRNGT error notifies and panics.

## Dependencies and Integration Points
It depends on OF compatibles `arm,cryptocell-713-trng` and `arm,cryptocell-703-trng`, `arm,rosc-ratio`, platform IRQ/MMIO, optional clock, runtime PM, hwrng core, FIPS hooks, and register definitions from `cctrng.h`.

## Risks
`cctrng_read()` ignores the `wait` parameter and returns only currently buffered bytes. `spin_trylock()` can cause short zero reads under concurrent consumers. Error handling cycles ROSCs but can stop refilling if no valid oscillator remains. FIPS CRNGT failure intentionally panics.

## Test Signals
Test missing/invalid `arm,rosc-ratio`, IRQ delivery, EHR valid path, autocorrelation/watchdog ROSC failover, zero EHR discard, concurrent reads, runtime suspend/resume, FIPS CRNGT path, and buffer wraparound.
