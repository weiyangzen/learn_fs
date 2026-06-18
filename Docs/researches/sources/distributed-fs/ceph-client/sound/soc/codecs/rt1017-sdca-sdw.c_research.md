# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.c

## Purpose
`rt1017-sdca-sdw.c` is the SoundWire SDCA ASoC driver for the Realtek RT1017 smart amplifier. Unlike the I2C codecs in this subset, it uses a 32-bit SoundWire SDCA regmap, SoundWire slave lifecycle callbacks, runtime PM, SoundWire stream/port configuration, and SDCA controls for power, mute, rate, and channel cluster selection.

## Important APIs, Types, And Functions
`struct rt1017_sdca_priv` stores the ASoC component, regmap, SoundWire slave, bus params, and hardware-init flags. `rt1017_sdca_sdw_probe()` creates the SoundWire regmap and calls `rt1017_sdca_init()`, which allocates state and registers the component and DAI. `rt1017_sdca_read_prop()` declares SoundWire properties: source port 2 for IV capture, sink port 1 for playback, full data ports, simple channel prepare, timeouts, paging support, and interrupt quirks. `rt1017_sdca_update_status()` triggers hardware init when the slave attaches.

ASoC DAI ops are `rt1017_sdca_pcm_hw_params()`, `rt1017_sdca_pcm_hw_free()`, `rt1017_sdca_set_sdw_stream()`, and `rt1017_sdca_shutdown()`. DAPM event callbacks control PDE23 power state, class-D PWM trim/class-D register, and feedback path register changes.

## Control Flow
SoundWire probe only initializes software state. Real hardware programming occurs in `rt1017_sdca_io_init()` after the slave reports attached. First init enables runtime PM and autosuspend; later init reopens the cache and bypasses it. The function writes a software reset, applies `rt1017_blind_write`, updates init flags, and drops the PM reference.

For PCM setup, the machine driver first supplies an SDW stream pointer through `.set_stream`. `hw_params()` selects SoundWire direction and port based on playback versus capture, builds stream and port configs from rate, width, and channels, calls `sdw_stream_add_slave()`, maps supported rates to SDCA FS indices, and writes the SDCA CS21 FS control. `hw_free()` removes the slave from the stream. DAPM routes DP1 playback through DAC and CLASS D to speaker output, and IV feedback generators through DP2 capture.

## State And Persistence
The regmap uses `REGCACHE_MAPLE` with 32-bit register addresses and 8-bit values. Runtime PM suspend sets cache-only when hardware was initialized; resume waits for SoundWire reinitialization when needed, then syncs the cache. `hw_init` is cleared on unattached status, while `first_hw_init` controls one-time runtime PM setup and later cache-bypass behavior.

## Dependencies And Integration Points
The driver depends on SoundWire core, SDCA register macros, runtime PM, ASoC, regmap SoundWire, and DAPM. It binds with `SDW_SLAVE_ENTRY_EXT(0x025d, 0x1017, 0x3, 0x1, 0)`. It integrates with machine drivers through the DAI named `rt1017-aif`, playback stream `DP1 Playback`, capture stream `DP2 Capture`, and SoundWire stream handoff.

## Risks
Hardware init is status-driven, so register access before attach can fail or be cached unexpectedly. `hw_params()` requires an SDW stream and `sdw_slave`; missing machine-driver setup returns `-EINVAL`. Only 44.1, 48, 96, and 192 kHz are mapped to SDCA FS codes. Blind writes are large and hardware-specific. Resume waits up to 5 seconds for SoundWire initialization and can return `-ETIMEDOUT`.

## Test Signals
Test SoundWire attach/unattach cycles, first and repeated hardware init, runtime suspend/resume with unattach request, playback and capture stream setup/removal, missing `.set_stream` failure, supported and unsupported rates, DAPM PDE/class-D/feedback event writes, and readable/volatile register coverage for SDCA controls.
