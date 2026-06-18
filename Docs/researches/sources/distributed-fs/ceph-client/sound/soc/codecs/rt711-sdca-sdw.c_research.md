# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca-sdw.c

## Purpose
`rt711-sdca-sdw.c` is the SoundWire bus wrapper for the Realtek RT711 SDCA codec. It defines normal and MBQ regmaps, readable/volatile register policies, SoundWire slave properties, SDCA interrupt processing, attach-triggered initialization, PM cache handling, and the `sdw_driver` binding that delegates codec behavior to the shared `rt711-sdca.c` implementation.

## Important APIs, Types, And Functions
Important callbacks are `rt711_sdca_sdw_probe()`, `rt711_sdca_sdw_remove()`, `rt711_sdca_update_status()`, `rt711_sdca_read_prop()`, `rt711_sdca_interrupt_callback()`, `rt711_sdca_dev_suspend()`, `rt711_sdca_dev_system_suspend()`, and `rt711_sdca_dev_resume()`. Two regmap configurations are defined: an 8-bit value SoundWire SDCA regmap with Maple cache and a 16-bit value MBQ regmap, also cached. The driver calls external shared-code functions `rt711_sdca_init()` and `rt711_sdca_io_init()` from `rt711-sdca.h`.

## Control Flow
Probe creates the MBQ regmap with `devm_regmap_init_sdw_mbq()`, creates the normal SDW regmap with `devm_regmap_init_sdw()`, and calls `rt711_sdca_init()`. `update_status` clears `hw_init` when unattached. When attached, it restores SDCA interrupt masks if jack detection has already been configured, then calls `rt711_sdca_io_init()` if hardware is not initialized.

`read_prop` advertises paging support, source ports 2 and 4, sink port 3, DP0 properties, simple channel-prepare state machines, 10 ms channel-prepare timeouts, 700 ms clock-stop timeout, invalid initial parity quirk, and wake capability. Interrupt handling cancels pending jack work, preserves a pending SDCA status byte when needed, locks `disable_irq_lock`, reads SDCA interrupt status registers, clears SDCA_0 and SDCA_8 flags with up to three retries, warns if flags remain, and schedules jack detection after 30 ms for SDCA cascades unless interrupts are disabled.

Suspend cancels jack works and places both regmaps in cache-only mode. System suspend additionally sets `disable_irq`, masks SDCA interrupt bits 0 and 8, and then calls the normal suspend path. Resume either re-enables SDCA masks immediately when the slave did not detach, or waits up to five seconds for SoundWire initialization after detach. It then clears `unattach_request`, disables cache-only mode, and syncs both regmaps.

## State And Persistence Behavior
The transport stores state in `struct rt711_sdca_priv` from the shared RT711 SDCA header: hardware init flags, slave pointer, jack work, interrupt-disable state, cached SDCA status bytes, regmaps, and calibration/IRQ locks. Normal and MBQ register spaces are cached separately. Interrupt status is preserved across canceled work through `scp_sdca_stat1` and `scp_sdca_stat2`, which avoids losing HID/jack ownership state when work is rescheduled.

## Dependencies And Integration Points
The file depends on SoundWire core, SDCA register macros, regmap, PM runtime, and the shared RT711 SDCA component implementation. It includes `rt711-sdca.h` for entity/control constants and shared private state, and `rt711-sdca-sdw.h` for default register tables. Its SoundWire id matches Realtek manufacturer `0x025d`, part `0x711`, SDCA class/revision tuple in `SDW_SLAVE_ENTRY_EXT()`.

## Risks
SDCA interrupt handling is race-sensitive: canceling delayed work, preserving status, clearing interrupt flags, and system-suspend masking must remain ordered. Both normal and MBQ caches must be synced on resume; missing one can leave controls stale. The driver restores SDCA interrupt masks on attach only if `hs_jack` is set, so jack setup timing matters. The long 700 ms clock-stop timeout and paging support are part of the hardware contract and should not be changed without SoundWire validation.

## Test Signals
Signals include SoundWire enumeration, successful `rt711_sdca_io_init()`, correct source/sink port discovery, SDCA interrupt delivery for jack/HID events, no stuck SDCA interrupt warnings, jack work scheduling after cascade interrupts, system/runtime suspend and resume with both regmaps synced, and no five-second resume timeout after detach/reattach.
