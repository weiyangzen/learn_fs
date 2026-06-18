# sources/distributed-fs/ceph-client/drivers/soundwire/intel_bus_common.c

## Purpose

`intel_bus_common.c` contains Intel bus lifecycle and bank-switch helpers shared by classic Intel and ACE2.x hardware ops. It coordinates Cadence soft reset/init, config update, interrupt enable, clock stop/restart, delayed enumeration, slave status clearing, link power-down, wake enable, and multi-link sync pre/post callbacks.

## Important APIs, types, and functions

- `intel_start_bus()` performs first startup after link power-up.
- `intel_start_bus_after_reset()` restarts after runtime resume with bus reset semantics and handles the clock-stop0 preservation case.
- `intel_check_clock_stop()` validates that Cadence reported clock-stop state.
- `intel_start_bus_after_clock_stop()` restarts from normal clock stop.
- `intel_stop_bus()` cancels enumeration, optionally enters clock stop, disables Cadence interrupts, powers down the link, and programs SHIM wake.
- `intel_pre_bank_switch()` and `intel_post_bank_switch()` arm and trigger hardware synchronized bank switches for multi-link streams.

## Control flow

Startup soft-resets Cadence, arms hardware sync for multi-link, initializes Cadence, issues config update, optionally triggers sync go, waits for config update to clear, enables interrupts, exits reset, checks self-clearing bits, and schedules delayed enumeration. Resume-after-reset is similar but either reinitializes from a non-clock-stop0 state or simply enables interrupts for preserved clock-stop0, then restarts the Cadence clock and schedules enumeration.

Stop flow cancels attach work first. If clock stop is requested, it asks Cadence to stop the clock and sets `wake_enable` only on success. It then disables interrupts, powers down the link through generation ops, and programs wake enable/disable based on whether clock stop succeeded.

Bank-switch callbacks are no-ops unless `bus->multi_link` is true. Pre-bank arms sync. Post-bank takes the shared SHIM lock and issues `SYNCGO` only if any CMDSYNC bit is still armed, so only the first master in the stream triggers the synchronized switch.

## State and persistence behavior

The file mutates Cadence bus state, interrupt state, delayed work, slave attachment status, clock-stop state, and hardware sync bits. It relies on `bus->multi_link`, `bus->hw_sync_min_links`, and generation-specific sync ops. Hardware state persists in Cadence MCP registers and Intel SHIM/HDA sync/wake state.

## Dependencies and integration points

It depends on Cadence helpers, generic SoundWire bus helpers (`sdw_clear_slave_status()`), Intel inline op wrappers, and common delayed enumeration work. It is called from Intel hardware ops tables and PM paths in `intel_auxdevice.c`.

## Risks and edge cases

- Error paths after partial startup may leave interrupts or config state partially enabled; callers must unwind power and PM.
- `intel_stop_bus()` returns before wake programming if interrupt disable or power-down fails.
- Resume-after-reset must correctly identify clock-stop0 preservation; clearing slave status unnecessarily can force avoidable reenumeration, while failing to clear can leave stale devices.
- Multi-link post-bank locking assumes all involved links share compatible `shim_lock` ordering.
- Delayed enumeration timing is fixed at 100 ms, which can be sensitive to slow peripherals.

## Test signals

Validate startup, stop with and without clock stop, resume after teardown, resume after bus reset, resume after normal clock stop, multi-link bank switching, single-link no-op bank switch, and failure injection for Cadence init/config-update/interrupt/clock operations. Check delayed work cancellation on stop and scheduling on every successful start path.
