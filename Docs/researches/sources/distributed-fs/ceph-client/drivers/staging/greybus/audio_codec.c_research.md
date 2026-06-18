# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.c

## Purpose

`audio_codec.c` implements an ASoC dummy codec for Greybus audio modules behind APBridgeA. It owns the global codec instance, per-DAI stream state, dynamic module registration/unregistration, jack creation, and the mapping from ASoC PCM/DAPM events to Greybus/APBridgeA protocol operations.

## Important APIs, Types, and Functions

Important exported functions are `gbaudio_module_update()`, `gbaudio_register_module()`, and `gbaudio_unregister_module()`. DAI callbacks are `gbcodec_startup()`, `gbcodec_shutdown()`, `gbcodec_hw_params()`, `gbcodec_prepare()`, and `gbcodec_mute_stream()`. Module stream helpers enable/disable TX/RX through APBridgeA CPort registration, Greybus PCM programming, Greybus TX/RX activation, and APBridgeA stream start/stop/shutdown. `gbcodec_probe()` initializes `struct gbaudio_codec_info` and the DAI parameter list.

## Control Flow

The platform codec registers one DAI named `apb-i2s0`. PCM startup records stream state and blocks suspend. `hw_params()` validates stereo, 48 kHz, S16_LE, sends APBridgeA I2S config, and caches Greybus PCM parameters. `prepare()` sets APBridgeA data size. `mute_stream()` starts or stops APBridgeA TX/RX. Dynamic module registration adds topology-provided DAPM widgets, routes, controls, and jack devices into the already-probed codec component. DAPM AIF widget events call `gbaudio_module_update()` to register CPorts, set PCM, activate/deactivate Greybus data paths, and unregister CPorts.

## State and Persistence Behavior

`gbcodec` is a single global pointer to the active codec info. It owns lists of registered modules and DAI stream parameters under mutexes. Each `gbaudio_data_connection` has playback/capture state values tracking shutdown/startup/hwparams/prepare/start/stop. Jack status and module topology state live in `struct gbaudio_module_info`.

## Dependencies and Integration Points

It integrates with ASoC component/DAI/DAPM/jack APIs, runtime PM, Greybus audio protocol helpers, APBridgeA helpers, topology parsing, and the audio manager/module driver. It is built as `gb-audio-codec.o`.

## Risks and Edge Cases

The global `gbcodec` design assumes one codec instance. Only one DAI is defined despite header constants for two. `module_state` is captured before each enable/disable sequence and not refreshed after state updates, so later blocks can run based on the original state; this is intentional for staged catch-up but can be confusing. Hard-coded I2S port `0`, data size `192`, MCLK `6144000`, and 48 kHz/S16/stereo limit flexibility. Error paths in partial stream enable may leave earlier APBridgeA/Greybus state active. Dynamic ASoC object removal manipulates lists manually and needs close review against current ASoC internals.

## Test Signals

Test module registration before/after card instantiation, no-codec and no-module cases, PCM parameter rejection, APBridgeA config failure, playback/capture start/stop, module unplug while streaming, jack/button registration cleanup, and multiple module attempts with one global codec.
