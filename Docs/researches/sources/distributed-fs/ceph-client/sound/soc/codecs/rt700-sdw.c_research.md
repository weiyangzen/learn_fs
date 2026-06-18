# sources/distributed-fs/ceph-client/sound/soc/codecs/rt700-sdw.c

## Purpose
`rt700-sdw.c` is the SoundWire transport driver for the Realtek RT700 codec. It creates SoundWire and logical codec regmaps, translates RT700 HD-A-style verb/index accesses over SoundWire, declares SoundWire slave capabilities, handles attach/detach status, interrupt scheduling, bus clock configuration, PM cache transitions, and binds the shared RT700 ASoC component implementation from `rt700.c`.

## Important APIs, Types, And Functions
The driver registers an `sdw_driver` named `rt700` with `rt700_slave_ops`. Important callbacks are `rt700_sdw_probe()`, `rt700_sdw_remove()`, `rt700_update_status()`, `rt700_read_prop()`, `rt700_bus_config()`, `rt700_interrupt_callback()`, `rt700_dev_suspend()`, `rt700_dev_system_suspend()`, and `rt700_dev_resume()`. The logical codec regmap uses 24-bit registers and 32-bit values with custom `rt700_sdw_read()` and `rt700_sdw_write()` callbacks; the raw `sdw_regmap` uses 32-bit addresses and 8-bit values with no cache.

## Control Flow
Probe initializes the raw SoundWire regmap with `devm_regmap_init_sdw()`, then initializes the logical cached regmap with custom read/write methods, and calls `rt700_init()` to allocate shared state and register the ASoC component/DAIs. `update_status` clears `hw_init` on unattached status and calls `rt700_io_init()` when the slave becomes attached and hardware has not been initialized. `read_prop` advertises source ports 2 and 4, sink ports 1 and 3, full data-port mode, simple channel-prepare state machines, wake capability, and a 20 ms clock-stop timeout.

The custom read/write callbacks are central. They distinguish plain SoundWire registers, HD-A verb ranges, right-channel amplifier addresses, 0x7000/0x9000 split high/low verb writes, 0xb000 pin-sense reads, and private indexed registers encoded above 16 bits. HD-A and indexed reads issue one or more SDW writes to trigger the codec operation, then collect the returned bytes from `RT700_READ_HDA_3..0`. Writes split 16-bit values into the high/low SDW command addresses required by the hardware.

Interrupts inspect implementation-defined control-port status and, unless `disable_irq` is set, schedule shared jack detection work. System suspend sets `disable_irq`, masks implementation-defined interrupts with `sdw_update_no_pm()`, cancels work, and makes the logical regmap cache-only. Resume waits up to five seconds for reinitialization when the slave detached, clears cache-only mode, and syncs selected logical register regions.

## State And Persistence Behavior
Transport state is stored in `struct rt700_priv` allocated by `rt700_init()`: `sdw_regmap`, logical `regmap`, `slave`, cached bus params, `hw_init`, `first_hw_init`, jack work, and interrupt-disable state. Register persistence is split: raw SoundWire accesses are uncached, while codec logical state uses Maple cache and is synchronized during resume. `hw_init` gates repeated initialization after attach; `first_hw_init` gates runtime PM/resume behavior once enumeration has happened at least once.

## Dependencies And Integration Points
The file depends on SoundWire core APIs, regmap, PM runtime, and the shared RT700 component APIs from `rt700.h`. It exposes no independent ALSA component; instead it bridges SoundWire enumeration to `rt700_init()`, `rt700_io_init()`, and `rt700_clock_config()`. The SoundWire device id matches Realtek manufacturer `0x025d`, part `0x700`, class/revision tuple in `SDW_SLAVE_ENTRY_EXT()`.

## Risks
The HD-A-over-SoundWire translation is delicate: address masks, index-register packing, and high/low byte ordering must match hardware. The read path writes through `*val` for some command setup, so callers must use initialized command payloads where required. Interrupt masking races are mitigated with `disable_irq_lock`, but changes around system suspend can lose jack events. Resume only syncs selected ranges, so adding cached registers outside those ranges may require resume updates. Port bitmaps and port-number assumptions must stay aligned with `rt700.c` DAI stream mapping.

## Test Signals
Useful tests include SoundWire enumeration and attach, successful `rt700_io_init()`, no regmap read/write translation errors, playback/capture over ports 1-4, jack interrupt scheduling, runtime/system suspend and resume with no timeout, cache sync restoring controls, and `rt700_clock_config()` accepting expected bus frequencies.
