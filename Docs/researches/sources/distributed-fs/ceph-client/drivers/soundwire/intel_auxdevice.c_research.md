# sources/distributed-fs/ceph-client/drivers/soundwire/intel_auxdevice.c

## Purpose

`intel_auxdevice.c` is the auxiliary-bus Intel SoundWire link driver. It binds each `soundwire_intel.link` auxiliary device into a Cadence-backed SoundWire master, reads generic and Intel-specific firmware properties, handles device-number allocation and wake-capable peripherals, starts DAIs and the bus, processes wake events, and owns runtime/system PM policy for Intel links.

## Important APIs, types, and functions

- Module parameters `sdw_md_flags` and `sdw_mclk_divider` control per-link PM/multi-link behavior and clock workarounds.
- `wake_capable_list`, `is_wake_capable()`, `intel_get_device_num_ida()`, and `intel_put_device_num_ida()` reserve higher device numbers for wake-capable parts.
- `sdw_master_read_intel_prop()` reads `intel-sdw-ip-clock`, `intel-quirk-mask`, and Intel timing properties from `mipi-sdw-link-N-subproperties`.
- `sdw_intel_ops` is the master ops table wiring Cadence transfers, bank-switch callbacks, device-number allocation, BPT hooks, DMI ADR override, and bus config.
- `intel_link_probe()` creates `struct sdw_intel`, initializes Cadence state, validates link count, calls `sdw_cdns_probe()`, and registers the SoundWire master.
- `intel_link_startup()` powers the link, registers DAIs, enables debugfs/runtime PM, starts the bus, applies clock-stop quirks, and marks `startup_done`.
- PM callbacks `intel_pm_prepare()`, `intel_suspend()`, `intel_suspend_runtime()`, `intel_resume()`, and `intel_resume_runtime()` implement Intel clock-stop, teardown, bus-reset, and full resume flows.
- `intel_link_process_wakeen_event()` handles shared WAKEEN events by disabling wake and requesting link resume.

## Control flow

Probe is two-stage. `intel_init.c` creates the auxiliary device, then this driver probes it and registers a SoundWire master with properties but does not necessarily start the hardware bus. Later, `sdw_intel_startup()` calls `intel_link_startup()` for enabled links after the Intel audio DSP is powered. Startup resolves module flags, enables multi-link synchronization if allowed, powers the link through generation-specific hw ops, registers DAIs, enables PM, starts the Cadence bus, applies no-clock-stop quirks, and idles runtime PM.

Runtime PM suspend chooses one of three flows from `clock_stop_quirks`: teardown powers the bus down without clock stop; bus reset requests clock stop plus reset on resume; no quirks uses normal clock stop and wake enable. Runtime resume disables wake, powers up if needed, clears slave status for reset/teardown paths, and restarts the bus using the matching common bus helper. System suspend disables runtime PM to avoid races and either handles an already suspended link or stops the bus without wake-based clock stop.

Wake events are dispatched from the parent context across link devices. A link ignores wake if disabled or not started, checks generation wake status, disables WAKEEN immediately, and requests runtime resume.

## State and persistence behavior

State includes `sdw->startup_done`, bus properties, Cadence bus lists, DAI runtime arrays, runtime PM state, `intel_peripheral_ida`, `bus->assigned`, and shared wake/device-number policy. Firmware-derived Intel properties are allocated with devm and stored in `bus->vendor_specific_prop`. PM transitions persist through hardware link power, clock-stop, WAKEEN, slave status, and Cadence bus reset state.

## Dependencies and integration points

This driver depends on the Linux auxiliary bus, Cadence SoundWire controller helpers, generic SoundWire bus/master APIs, DMI ADR override, PM runtime, ASoC component registration through generation ops, Intel public resource callbacks, and firmware DisCo properties. It is the central bridge between `intel_init.c`, `intel.c`/`intel_ace2x.c`, `intel_bus_common.c`, and the generic SoundWire bus core.

## Risks and edge cases

- `intel_prop_read()` ignores the return from `sdw_master_read_intel_prop()`, so missing Intel-specific properties may be reported but not fatal.
- Wake-capable parts rely on both firmware `wake_capable` and a hard-coded ID list; stale lists can assign the wrong device-number range.
- Runtime PM reference handling differs when `clock_stop_quirks` is zero versus nonzero and when module flags disable PM.
- System suspend handles failures leniently in `.prepare` to avoid blocking suspend, so recovery depends on resume paths.
- The PM paths assume parent PCI/DSP power sequencing makes SHIM/HDA registers accessible at the right time.
- Bus restart paths must match the exact suspend mode or slaves may retain stale status/device numbers.

## Test signals

Test probe with enabled, disabled, and out-of-range link ids; firmware with and without Intel subproperties; wake-capable and non-wake-capable peripherals; module flags disabling PM, idle, clock stop, and multi-link; runtime suspend/resume for teardown, bus-reset, and clock-stop modes; wake IRQ flooding; system suspend while a stream is paused; and cleanup/unbind while children are runtime suspended.
