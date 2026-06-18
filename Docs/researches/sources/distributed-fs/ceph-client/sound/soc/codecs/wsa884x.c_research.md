# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa884x.c

## Purpose
`wsa884x.c` is the ASoC SoundWire codec driver for Qualcomm WSA884x speaker amplifiers. It provides a mono `SPKR` playback DAI, register-cache backed initialization for the amplifier, six selectable SoundWire sink ports, speaker/receiver mode tuning, PA mute and DAPM power sequencing, regulator/reset handling, and an optional hwmon temperature input.

## Important APIs, Types, And Functions
`struct wsa884x_priv` stores the SoundWire slave, regmap, two bulk regulators (`vdd-io`, `vdd-1p8`), reset or `powerdown` GPIO, stream runtime/config, per-port controls, mode, init flag, and protected temperature/PA fields. Important functions include `wsa884x_probe()`, `wsa884x_init()`, `wsa884x_set_gain_parameters()`, `wsa884x_update_status()`, `wsa884x_port_prep()`, `wsa884x_hw_params()`, `wsa884x_hw_free()`, `wsa884x_mute_stream()`, `wsa884x_spkr_event()`, `wsa884x_get_temp()`, and runtime PM callbacks. The register surface is defined by `wsa884x_regmap_config`, `wsa884x_defaults`, and `wsa884x_reg_init`.

## Control Flow
Probe allocates state, gets/enables both regulators, installs a devm regulator-disable action, obtains reset control or legacy powerdown GPIO, initializes SoundWire stream parameters, parses optional `qcom,port-mapping`, advertises sink ports and interrupts to SoundWire, deasserts reset, builds a SoundWire regmap, starts in cache-only mode until enumeration, registers optional hwmon, enables runtime PM, and registers the component and DAI. On SoundWire `ATTACHED`, `wsa884x_update_status()` leaves cache-only mode, syncs cached defaults, and calls `wsa884x_init()` unless already initialized; on `UNATTACHED`, it marks the cache dirty and clears `hw_init`. `wsa884x_init()` applies the init sequence, detects haptics SKU through OTP ID, writes analog workorder controls, then applies speaker/receiver gain parameters. ALSA controls set mode and enabled ports. `hw_params()` builds active SoundWire port config and calls `sdw_stream_add_slave()`. DAPM speaker power-up sets PA state, applies mode/current-limit tuning, and enables PDM watchdog; power-down disables the watchdog and clears PA state. Mute toggles DRE gain and global PA enable.

## State And Persistence
The driver intentionally keeps regmap cache-only until the SoundWire device is enumerated, then uses cache sync as part of attachment. Runtime suspend also switches to cache-only and marks the cache dirty; resume syncs hardware from cache. `port_enable[]` and `dev_mode` are user-visible ALSA-control state. Temperature state is cached and mutex protected so hwmon reads can return a previous valid value when the PA is active.

## Dependencies And Integration Points
It integrates with SoundWire ID `0x0217:0x204`, regmap SoundWire, ASoC controls/DAPM/DAI, runtime PM, regulator bulk APIs, reset or GPIO descriptor APIs, optional hwmon, and DT `qcom,port-mapping`. The six sink ports are DAC, COMP, BOOST, PBR, VISENSE, and CPS with fixed channel masks.

## Risks And Edge Cases
No local validation prevents enabling zero ports before stream setup. Several regmap updates in init, gain setup, DAPM, mute, and temperature paths ignore return values, so hardware misprogramming may be hard to diagnose. `port_prep()` trusts SoundWire port numbers for array indexing. Temperature reads discard implausible values and can return `-EAGAIN`, which is expected before valid trim/sample data exist. Cache-only startup depends on proper SoundWire status transitions; missing `ATTACHED` handling would leave writes cached but not applied. Legacy `powerdown-gpios` cannot handle shared reset semantics as robustly as reset controllers.

## Test Signals
Tests should cover regulator acquisition/enabling and cleanup, reset-controller versus GPIO reset paths, SoundWire unattached/attached transitions and regcache sync, SKU-dependent init, speaker versus receiver gain/current-limit settings, each SoundWire port switch, stream add/remove with selected ports, mute/unmute PA state, DAPM power-up/down sequencing, runtime suspend/resume cache behavior, hwmon reads with PA off/on, invalid trim values, missing/partial DT port mapping, and probe deferral from supplies or reset resources.
