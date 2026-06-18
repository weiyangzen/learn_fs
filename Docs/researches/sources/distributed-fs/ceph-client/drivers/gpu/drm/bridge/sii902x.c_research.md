# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sii902x.c

## Purpose

`sii902x.c` drives Silicon Image SII902x RGB-to-HDMI transmitters, especially `sil,sii9022`. It is a DRM HDMI bridge with optional legacy connector creation, HPD/EDID support, a DDC I2C mux implemented through the transmitter pass-through mode, and optional HDMI audio codec registration for I2S audio.

## Important APIs, Types, And Functions

`struct sii902x` stores the I2C client, unlocked regmap, DRM bridge/connector, reset GPIO, DDC mux, input bus width, a mutex shared by video/audio/DDC register sequences, and audio state containing codec platform device, optional `mclk`, and I2S FIFO mappings.

Important DRM callbacks are `sii902x_bridge_attach()`, `sii902x_bridge_mode_set()`, `sii902x_bridge_atomic_enable()/disable()`, `sii902x_bridge_detect()`, `sii902x_bridge_edid_read()`, `sii902x_bridge_atomic_get_input_bus_fmts()`, `sii902x_bridge_atomic_check()`, and `sii902x_bridge_mode_valid()`. Connector callbacks provide detect/get-modes when the bridge creates its own connector. Audio is exposed through `hdmi_codec_ops`: `sii902x_audio_hw_params()`, `audio_shutdown()`, `audio_mute()`, `audio_get_eld()`, and `audio_get_dai_id()`.

## Control Flow

Probe checks SMBus byte support, allocates state, creates an I2C regmap with locking disabled, obtains optional reset GPIO, reads input `bus-width` from port 0, optionally finds a downstream bridge from port 1, initializes the mutex, enables `iovcc` and `cvcc12`, then runs `sii902x_init()`.

Initialization resets the chip, writes TPI request byte, validates chip ID byte 0 as `0xb0`, clears pending interrupts, enables/request HPD IRQ when present, initializes optional HDMI codec, creates a one-channel I2C mux for DDC, sets bridge OF node/timings/type/ops, enables HPD ops if IRQ-backed, and adds the bridge.

Mode set writes TPI video timing bytes derived from adjusted mode, builds an AVI infoframe, and writes the packed payload minus the HDMI header but with checksum. Atomic enable selects HDMI vs DVI from connector display info, exits D0 power state, and clears powerdown; disable sets powerdown. EDID reads lock the shared mutex and use the mux adapter, whose select/deselect callbacks request and release the DDC bus using raw SMBus transfers because the parent adapter lock is already held.

## State And Persistence Behavior

The driver maintains no persistent configuration beyond DT-derived bus width, downstream bridge pointer, audio lane mapping, and connector ELD. Hardware registers are volatile and uncached. The mutex preserves atomicity of multi-register sequences across video, audio, HPD, and DDC paths. Audio `mclk` is prepared during hw_params and disabled on shutdown or error.

## Dependencies And Integration Points

Dependencies include DRM bridge/connector/EDID helpers, regmap, I2C mux, GPIO, regulator, optional clock, and ASoC HDMI codec APIs. It integrates with OF graph ports for RGB input and optional downstream bridge output, `#sound-dai-cells` plus `sil,i2s-data-lanes` for audio, and DRM HPD notification when an IRQ is available.

## Risks

DDC pass-through is delicate: select/deselect must avoid regmap locking and touch only DDC request/grant bits in `SII902X_SYS_CTRL_DATA`. Mode support is capped to 25-165 MHz pixel clock. `sii902x_bridge_atomic_get_input_bus_fmts()` leaks its allocation if an unsupported `bus_width` is configured because it returns NULL after allocating. Audio sample-rate table uses 44000 and 88000 entries, which look suspicious for 44.1/88.2 kHz style rates. Shared register access relies on callers consistently taking `mutex`.

## Test Signals

Useful tests include probe/chip ID validation, connector HPD IRQ and polling behavior, EDID reads through the mux including timeout/release paths, mode validation around clock limits, HDMI/DVI output-mode selection, AVI infoframe programming, 16/18/24-bit input bus format negotiation, I2S audio startup/shutdown/mute and ELD readback, and remove cleanup of bridge, mux, and codec device.
