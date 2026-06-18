# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa881x.c

## Purpose

`wsa881x.c` implements the Qualcomm WSA881x SoundWire smart speaker amplifier codec driver. It defines the digital/analog register map, reset defaults and revision patches, SoundWire port properties, ASoC controls and DAPM widgets, speaker amplifier power sequencing, VI-sense support, runtime PM over shutdown GPIO/regcache, and SoundWire driver probe/status/port/bus callbacks.

## Important APIs, Types, and Functions

- Register definitions and data tables: `WSA881X_*` register macros, `wsa881x_defaults`, `wsa881x_rev_2_0`, `wsa881x_pre_pmu_pa_2_0`, and `wsa881x_vi_txfe_en_2_0`.
- SoundWire topology: `enum wsa_port_ids`, `wsa_sink_dpn_prop`, and `wsa881x_pconfig` describe DAC, COMP, BOOST, and VISENSE sink ports.
- `struct wsa881x_priv`: persistent driver state with regmap, device/slave pointers, stream config/runtime, selected port configs, optional shutdown GPIO, active port count, hardware-init flag, and per-port prepared/enabled flags.
- Regmap filters: `wsa881x_readable_register`, `wsa881x_volatile_register`, and `wsa881x_regmap_config`.
- Initialization and lifecycle: `wsa881x_init`, `wsa881x_probe`, `wsa881x_component_probe`, `wsa881x_update_status`, `wsa881x_runtime_suspend`, and `wsa881x_runtime_resume`.
- Controls: `wsa881x_put_pa_gain`, `wsa881x_get_port`, `wsa881x_set_port`, `wsa881x_boost_ctrl`, and `wsa881x_snd_controls`.
- DAPM/DAI: `wsa881x_spkr_pa_event`, `wsa881x_visense_txfe_ctrl`, `wsa881x_visense_adc_ctrl`, widgets/routes, `wsa881x_hw_params`, `wsa881x_hw_free`, `wsa881x_set_sdw_stream`, and `wsa881x_digital_mute`.
- SoundWire ops: `wsa881x_port_prep` and `wsa881x_bus_config`.

## Control Flow

SoundWire probe allocates private data, gets the optional `powerdown` GPIO, applies a backwards-compatibility inversion for historical DT polarity, initializes SoundWire stream parameters for 48 kHz mono PDM RX, publishes sink port properties, powers the device out of shutdown, creates an SDW regmap, enables runtime PM autosuspend, and registers the ASoC component and `SPKR` DAI.

When the SoundWire slave reports `SDW_SLAVE_ATTACHED` with a valid device number, `wsa881x_update_status` calls `wsa881x_init` once. Initialization registers the revision 2.0 patch, enables SoundWire reset output, releases analog and digital reset, applies clock/OCP/boost/speaker/protection tuning, reads OTP to choose a boost preset tweak, and marks `hw_init`. If the slave becomes unattached, `hw_init` is cleared so the sequence can run again.

User controls enable logical SoundWire ports and boost. `wsa881x_hw_params` builds a compact list of enabled `sdw_port_config` entries and calls `sdw_stream_add_slave`; `hw_free` removes the slave from the stream. `port_prep` tracks prepared ports by SoundWire port number, and the speaker DAPM event uses VISENSE prepared state to enable voltage/current sensing frontend and ADCs after speaker power-up, then disables them after power-down.

The PA gain control resumes the device, waits, then ramps gain incrementally in hardware-required steps with 1 ms sleeps. The speaker PA event enables OCP, applies pre-PMU PA writes, selects register-controlled gain, and holds OCP after power-down. Digital mute gates `WSA881X_SPKR_DRV_EN` bit 7.

Runtime suspend drives the shutdown GPIO to the logical shutdown value, makes regcache cache-only, and marks it dirty. Runtime resume deasserts shutdown, waits for SoundWire initialization completion with a 1 second timeout, disables cache-only mode, and syncs the regcache.

## State and Persistence Behavior

Persistent state includes the selected port-enable flags, port-prepared flags, active SoundWire stream runtime, `hw_init`, shutdown GPIO polarity workaround state, and regmap cache. Register values are cached with MAPLE regcache and resynchronized after runtime resume. `hw_init` is intentionally reset when the SoundWire slave detaches.

The shutdown GPIO is logical-state based: `sd_n_val` is high-for-shutdown/low-for-enable after the compatibility inversion. Port enable controls persist independently of stream start; `hw_params` snapshots them into `active_ports`.

## Dependencies and Integration Points

The driver depends on Linux SoundWire slave/regmap APIs, runtime PM, GPIO descriptors, ASoC component/DAI/DAPM/control APIs, and Qualcomm WSA881x SoundWire device IDs `0x0217:0x2010` and `0x0217:0x2110`. Machine drivers use the `SPKR` DAI and DAPM pins `IN` and `SPKR`.

## Risks and Edge Cases

- The shutdown GPIO polarity workaround intentionally supports old DTBs but can mis-handle rare correctly flagged active-high designs.
- `wsa881x_hw_params` does not reject zero enabled ports before calling `sdw_stream_add_slave`.
- `wsa881x_put_pa_gain` calls `pm_runtime_put_autosuspend` even when resume returned `-EACCES`; this may be acceptable for disabled PM but is a path to watch.
- Register patch/init errors from `regmap_register_patch` and many `regmap_update_bits` calls are ignored.
- Runtime resume depends on SoundWire `initialization_complete`; timeout shuts the device back down and returns `-ETIMEDOUT`.
- VISENSE enable depends on `port_prepared[VISENSE]`, not the separate user port-enable flag.

## Test Signals

Signals include SoundWire enumeration and component registration, revision patch writes on first attach and after detach/reattach, runtime suspend/resume GPIO and regcache behavior, 48 kHz mono playback stream setup with enabled ports, port switch controls reflected in `sdw_stream_add_slave`, boost switch writes and delay, PA gain ramp writes, DAPM speaker power sequence with OCP and VISENSE states, digital mute gating, and handling of initialization-complete timeout. No local KUnit tests are present.
