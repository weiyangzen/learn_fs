# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa883x.c

## Purpose
`wsa883x.c` is an ASoC codec driver for Qualcomm WSA883x SoundWire smart speaker amplifiers. It exposes one mono playback DAI named `SPKR`, initializes a large regmap-backed analog/digital register set, configures selectable SoundWire sink ports, controls the speaker power-amplifier path through DAPM and mute callbacks, and optionally registers a hwmon temperature sensor used by speaker-protection logic.

## Important APIs, Types, And Functions
The central state is `struct wsa883x_priv`, which keeps the SoundWire slave, regmap, regulator, reset or powerdown GPIO, stream config/runtime, port enable/prepared state, active port array, mode and compander offset controls, runtime-init state, and temperature/PA state protected by `sp_lock`. Key callbacks are `wsa883x_probe()`, `wsa883x_update_status()`, `wsa883x_port_prep()`, `wsa883x_hw_params()`, `wsa883x_hw_free()`, `wsa883x_set_sdw_stream()`, `wsa883x_digital_mute()`, `wsa883x_spkr_event()`, `wsa883x_get_temp()`, and runtime PM suspend/resume. `wsa883x_regmap_config`, `wsa883x_defaults`, and `reg_init` define the register cache and startup programming.

## Control Flow
Probe allocates state, enables `vdd`, obtains reset control or legacy `powerdown-gpios`, sets SoundWire properties and optional static port mapping, deasserts reset, creates a SoundWire regmap, registers hwmon when available, enables runtime PM, and registers the component/DAI. SoundWire attachment invokes `wsa883x_update_status()`, which runs `wsa883x_init()` once per attachment to read variant/version IDs, apply `reg_init`, and select a default compander offset. ALSA controls choose mode and enabled SoundWire ports. `hw_params()` compresses enabled ports into `port_config[]`, records the frame rate, and adds the SoundWire slave to the stream; `hw_free()` removes it. DAPM speaker events set PA-on state, tune receiver versus speaker path registers, enable VBAT filtering and PDM watchdog on power-up, and undo those settings on power-down. Mute toggles DRE gain and global PA enable.

## State And Persistence
Persistent state is devm-managed and mostly mirrored in regmap cache. `hw_init` is cleared on SoundWire unattached status and set after initialization. `port_enable[]`, `dev_mode`, and `comp_offset` are ALSA-control state that directly affect later stream and DAPM programming. Runtime PM switches the regmap into cache-only mode on suspend, marks it dirty, and syncs on resume. Temperature reads cache the last valid value and return it while the PA is on because direct temperature sampling is only safe when the amplifier is off.

## Dependencies And Integration Points
The driver depends on the SoundWire bus, regmap SoundWire backend, ASoC component/DAI/DAPM/control APIs, regulator framework, optional reset controller or `powerdown` GPIO, runtime PM, optional hwmon, and DT property `qcom,port-mapping`. It binds through SoundWire ID `0x0217:0x0202` and advertises simple clock-stop capability, sink ports, and SoundWire SCP interrupt masks.

## Risks And Edge Cases
The port mixer controls can leave no ports enabled, making `sdw_stream_add_slave()` operate with zero active ports. `port_prep()` indexes `prepare_ch->num - 1` without local bounds checks, relying on SoundWire core validity. Regmap writes in init and DAPM paths are mostly not checked, so hardware programming failures can be silent. Temperature conversion ignores intermediate read/update failures and filters only by plausible range; stale cached values are expected while PA is active. Regulator disable is handled manually only on probe failure, while reset is devm action based.

## Test Signals
Useful tests cover SoundWire probe and attachment, unattached reinitialization, reset-controller and legacy GPIO paths, missing `vdd`, static and absent `qcom,port-mapping`, toggling each port switch before `hw_params()`, stream add/remove with enabled ports, receiver/speaker DAPM register differences, mute/unmute register writes, runtime suspend/resume cache behavior, hwmon reads while PA is off/on, invalid OTP trim data, and variant-specific compander offset programming.
