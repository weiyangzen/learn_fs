# sources/distributed-fs/ceph-client/drivers/thermal/da9062-thermal.c

## Purpose
Dialog DA9062/DA9061 PMIC thermal TJUNC driver. It reports a synthetic thermal zone based on the PMIC over-temperature event bit, disables the IRQ during an event, polls until the event clears, and raises thermal updates for a HOT trip at 125C.

## Important APIs, Types, and Functions
- `struct da9062_thermal` stores parent PMIC pointer, delayed work, thermal zone, lock-protected temperature, IRQ, config, and device.
- `da9062_thermal_poll_on()` clears/reads `DA9062AA_EVENT_B`, sets temperature to 125C while `E_TEMP` is asserted or 0C when cleared, updates the thermal zone, requeues or re-enables IRQ.
- `da9062_thermal_irq_handler()` disables the IRQ and queues the work immediately.
- `da9062_thermal_get_temp()` returns the cached temperature under mutex.
- Probe registers a thermal zone with a single HOT trip and requests the named `THERMAL` IRQ.

## Control Flow
Probe reads optional `polling-delay-passive`, clamps it to 1-10 seconds, allocates state, initializes work and mutex, registers/enables the thermal zone, retrieves the PMIC IRQ by name, and requests a threaded IRQ. On IRQ, the handler disables the line and queues work. The work clears and rereads the status bit: if still hot it caches 125C, notifies the core, and requeues after the polling period; otherwise it caches 0C, notifies, and re-enables IRQ.

## State and Persistence
The only temperature state is a cached binary value, protected by `lock`. `pp_tmp` is a module-global polling period that can be changed from DT at probe. Hardware event state persists in PMIC registers.

## Dependencies and Integration Points
Depends on the DA9062 MFD parent, regmap, named platform IRQ, thermal core, delayed work on `system_freezable_wq`, and a fixed HOT trip.

## Risks and Edge Cases
- Temperature is binary, not an actual sensor reading; consumers must interpret it as event state.
- `pp_tmp` is global, so multiple instances would share the last parsed polling period.
- The IRQ is requested with non-devm `request_threaded_irq()`, so remove must free it.
- Work re-enables IRQ only after the event clears or error paths; repeated regmap failures may re-enable without updated cached temperature.

## Test Signals
Tests should simulate IRQ, persistent hot status requeue, clear status re-enable, DT polling bounds, thermal zone enable failure cleanup, IRQ request failure, and remove cancel/free/unregister ordering.
