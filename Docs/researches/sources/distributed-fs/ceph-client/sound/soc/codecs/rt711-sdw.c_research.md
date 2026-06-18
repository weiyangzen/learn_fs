# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdw.c

Purpose: Provides the SoundWire bus driver for the non-SDCA RT711 codec. It builds two regmaps, translates HDA-style register operations over SoundWire, declares port properties, handles attach status and interrupts, and manages runtime/system PM.

Important APIs and functions: `rt711_sdw_probe()` creates a raw SoundWire 8-bit regmap plus a logical 24/32-bit codec regmap with custom `rt711_sdw_read()`/`rt711_sdw_write()` callbacks, then calls `rt711_init()`. `rt711_read_prop()` advertises source ports 2 and 4 and sink port 3. `rt711_update_status()` calls `rt711_io_init()` on attach and clears `hw_init` on unattach. `rt711_bus_config()` stores bus params and calls `rt711_clock_config()`. `rt711_interrupt_callback()` schedules jack detection on implementation-defined control-port interrupts.

Control flow: Logical regmap reads/writes decide whether the target is an index register, HDA verb, gain register, or plain SoundWire register and emit the required low-level byte transactions. Interrupts are guarded by `disable_irq_lock` so system suspend can disable new scheduling while existing delayed work drains. Suspend cancels jack/button/calibration work and switches the logical regmap cache-only. Resume waits for SoundWire initialization if the slave was unattached, reenables interrupts if needed, clears `unattach_request`, and syncs selected regcache regions.

State and persistence: This file owns bus-visible properties and PM behavior while `rt711.c` owns codec semantics. Persistent state includes `params` copied from the bus, `disable_irq`, `hw_init`, `first_hw_init`, and regcache dirty/cache-only status.

Dependencies and integration: Integrates with `module_sdw_driver`, SoundWire slave ops, regmap, runtime PM, and `rt711.h`/`rt711-sdw.h`. It exposes SDW ID `0x025d:0x711` and the driver name `rt711`.

Risks and test signals: The custom HDA-over-SDW translation is fragile; bad register classification can corrupt codec state. Tests should exercise readable/volatile ranges, bus frequency changes, attach/unattach cycles, jack interrupts, system suspend with pending work, runtime resume cache sync, and probe failure paths for both regmaps.
