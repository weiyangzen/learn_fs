# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-sdw.c

## Purpose

`cs42l42-sdw.c` is the SoundWire bus glue for the Cirrus Logic CS42L42 ASoC codec. It adapts the common CS42L42 core in `cs42l42.c` to the SoundWire transport by providing SoundWire register access, SoundWire DAI stream setup, port preparation power hooks, attach/unattach handling, and runtime/system PM behavior. It replaces the normal ASP DAPM routes with SoundWire SRC routes and exports no public APIs of its own beyond the module driver.

## Important APIs, Types, and Functions

- `cs42l42_sdw_dai_startup()` refuses PCM startup until `init_done` is true, preventing ALSA streams before SoundWire enumeration and common codec initialization.
- `cs42l42_sdw_dai_hw_params()` converts ALSA params into `sdw_stream_config` and `sdw_port_config`, chooses DP2 for playback and DP1 for capture, calls `sdw_stream_add_slave()`, caches `sample_rate`, and configures SRC clocks through `cs42l42_src_config()`.
- `cs42l42_sdw_dai_prepare()` validates that both SoundWire-derived `sclk` and `sample_rate` are known, then calls `cs42l42_pll_config()`.
- `cs42l42_sdw_dai_hw_free()` removes the slave from the SoundWire stream and clears `sample_rate`.
- `cs42l42_sdw_port_prep()` powers headphone or ADC blocks around SoundWire port prepare/deprepare using `CS42L42_PWR_CTL1`.
- `cs42l42_sdw_read()` and `cs42l42_sdw_write()` implement custom regmap bus access. Registers are offset by `0x8000`; reads handle both immediate and delayed SoundWire memory-read completion through `MEM_ACCESS_STATUS`.
- `cs42l42_sdw_read_prop()`, `cs42l42_sdw_update_status()`, and `cs42l42_sdw_bus_config()` are the `sdw_slave_ops`.
- `cs42l42_sdw_runtime_suspend()`, `cs42l42_sdw_runtime_resume()`, and `cs42l42_sdw_resume()` manage cache-only regmap mode and SoundWire reattach recovery.
- `cs42l42_sdw_probe()` allocates private state, obtains IRQ from ACPI/DT, clones the shared regmap/component definitions for SoundWire-specific changes, enables runtime PM, and calls `cs42l42_common_probe()`.

## Control Flow

Probe allocates `struct cs42l42_private`, discovers an optional hardware IRQ, clones `cs42l42_regmap`, changes it to 16-bit register addressing with custom SoundWire read/write callbacks, starts in cache-only mode, clones `cs42l42_soc_component`, swaps DAPM routes to the SoundWire map, initializes runtime PM, and delegates resource/power/component registration to `cs42l42_common_probe()`.

SoundWire enumeration drives the real initialization. `update_status(ATTACHED)` ignores stale first attach reports while `sdw_waiting_first_unattach` is set. After a real attach, `cs42l42_sdw_init()` disables cache-only mode, calls `cs42l42_init()`, syncs cache writes that happened before attach, disables conditional clock-stop logic, and releases the probe-time runtime PM reference. `update_status(UNATTACHED)` is used during probe synchronization to release reset after the SoundWire core has seen the device absent.

PCM setup flows through the DAI ops: machine driver supplies an `sdw_stream` via `.set_stream`, `hw_params` adds the slave port, `bus_config` records `sclk` as half the current data rate, and `prepare` configures the shared PLL. Teardown removes the stream and resets `sample_rate`.

## State and Persistence Behavior

The file mutates shared `cs42l42_private` fields: `sdw_peripheral`, `sample_rate`, `sclk`, `sdw_waiting_first_unattach`, `init_done`, and runtime PM state. Regmap cache is the persistence boundary across pre-enumeration, runtime suspend, and system suspend. Cache writes are held until attach, then synced. After a SoundWire bus reset/unattach, `cs42l42_sdw_handle_unattach()` waits for `initialization_complete`, performs a soft reboot through a bypassed regmap write, sleeps for boot time, and marks the cache dirty before restore.

## Dependencies and Integration Points

This file depends on the Linux SoundWire core, ASoC DAI/component APIs, `sound/sdw.h` helpers, regmap custom bus callbacks, runtime PM, ACPI/OF IRQ discovery, and the common CS42L42 core exports in namespace `SND_SOC_CS42L42_CORE`. Build integration is through `CONFIG_SND_SOC_CS42L42_SDW` and `snd-soc-cs42l42-sdw.o`.

## Risks

Register access is timing-sensitive because delayed SoundWire reads poll very short intervals. Incorrect cache-only transitions can lose pre-attach configuration or attempt bus I/O while the manager is suspended. The driver rejects SoundWire clock changes while `stream_use` is nonzero; missing that guard can glitch active audio. Attach/unattach sequencing is subtle because stale ATTACH notifications after reset are explicitly filtered. `cs42l42_sdw_runtime_resume()` has a branch for `ret > 0`, but `cs42l42_sdw_handle_unattach()` currently returns only 0 or negative, so debounce waiting appears unreachable.

## Test Signals

Useful tests include SoundWire enumeration with stale attach conditions, runtime suspend/resume with regcache sync, system suspend while attached and after bus reset, playback and capture on DP2/DP1, unsupported clock/sample-rate combinations returning errors in `prepare`, and jack IRQ handling after SoundWire PM transitions. Build with `CONFIG_SND_SOC_CS42L42_CORE` and `CONFIG_SND_SOC_CS42L42_SDW`.
