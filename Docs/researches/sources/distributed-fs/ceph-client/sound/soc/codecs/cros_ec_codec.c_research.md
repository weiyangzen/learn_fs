# sources/distributed-fs/ceph-client/sound/soc/codecs/cros_ec_codec.c

## Purpose
This file is the ChromeOS Embedded Controller audio codec driver. It uses ChromeOS EC host commands to control EC audio functions: digital microphone gain, an EC I2S RX capture path, wake-on-voice enablement, hotword model loading, and a software PCM stream fed from EC audio data.

## Important APIs, types, and functions
The central type is `struct cros_ec_codec_priv`, shared by both registered ASoC components. It stores the EC device, capability bits, EC and AP shared-memory windows, DMIC probe state, I2S bit-clock ratio, wake-on-voice state, mapped WoV shared-memory pointers, an in-kernel circular audio queue, PCM DMA offset, a delayed work item, and a ChromeOS EC notifier.

All EC communication funnels through `send_ec_host_command()`. DMIC controls use `dmic_get_gain()`, `dmic_put_gain()`, and `dmic_probe()`. I2S capture setup uses `i2s_rx_hw_params()`, `i2s_rx_set_bclk_ratio()`, `i2s_rx_set_fmt()`, and `i2s_rx_event()`. Wake-on-voice support is implemented by `wov_map_shm()`, `wov_read_audio_shm()`, `wov_read_audio()`, `wov_copy_work()`, `wov_enable_get()`, `wov_enable_put()`, `wov_hotword_model_put()`, `wov_host_event()`, `wov_probe()`, `wov_remove()`, and PCM callbacks `wov_pcm_open()`, `wov_pcm_hw_params()`, `wov_pcm_hw_free()`, `wov_pcm_pointer()`, and `wov_pcm_new()`.

## Control flow
Platform probe allocates private state, discovers optional EC and AP shared-memory ranges from device tree, sends `EC_CODEC_GET_CAPABILITIES`, resets EC I2S RX using `EC_CODEC_I2S_RX_RESET`, and registers two ASoC components. The I2S RX component provides the `EC Codec I2S RX` DAI and DAPM path from `DMIC` to `I2S RX`; its probe also adds EC mic gain controls if max-gain querying works. The WoV component provides the `Wake on Voice` capture DAI, the `Wake-on-Voice Switch`, and the `Hotword Model` bytes control.

For I2S capture, `hw_params` accepts only 48 kHz with 16- or 24-bit samples, sends sample depth to the EC, then computes and sends BCLK either from the stored ratio or ALSA parameters. DAPM PRE_PMU sends EC enable and PRE_PMD sends EC disable. For wake-on-voice, probe registers an EC event notifier and maps optional language/audio shared memory. A WoV host event schedules delayed copy work. The worker reads audio through shared memory offsets or repeated host commands, enqueues bytes into a 64 KiB ring, drains full periods to ALSA's vmalloc DMA buffer, advances the PCM pointer, and calls `snd_pcm_period_elapsed()`.

Hotword model updates arrive as a bytes TLV control. The driver skips the TLV header, copies the model from userspace, hashes it with SHA-256, compares the current EC model hash, and sends the new model either through shared memory or chunked host commands.

## State and persistence behavior
State is volatile and split between the kernel private object, EC firmware state, and optional shared memory. `wov_enabled` mirrors EC wake-on-voice state after successful enable/disable commands. `ap_shm_last_alloc` is a monotonic allocator within the reserved AP shared-memory region during driver lifetime. WoV PCM state uses `wov_rp`, `wov_wp`, and `wov_dma_offset`; `wov_burst_read` causes initial larger reads after `hw_params`. The hotword model is persisted, if at all, by EC firmware, not by this driver.

## Dependencies and integration points
The file depends on ChromeOS EC protocol definitions, EC parent driver data from `dev_get_drvdata(pdev->dev.parent)`, optional OF reserved-memory mappings, ACPI ID `GOOG0013`, OF compatible `google,cros-ec-codec`, ASoC component/DAI/PCM APIs, SHA-256 hashing, delayed work, and the EC event notifier chain. User-visible integration is through the I2S capture DAI, WoV capture DAI, mic gain control, wake-on-voice switch, and hotword model bytes control.

## Risks and test signals
Risks include EC firmware capability mismatches, shared-memory size or type errors, host-command latency in audio paths, ring-buffer overrun during WoV bursts, TLV model size assumptions, and synchronization between `wov_copy_work()` and PCM teardown. `wov_hotword_model_put()` subtracts the TLV header from `size`, so malformed or too-small control payload handling should be validated. `wov_pcm_hw_free()` drains queued bytes before clearing the substream, which can emit period elapsed during teardown.

Useful test signals are successful capability query and I2S reset, graceful old-firmware `-ENOPROTOOPT` reset handling, DMIC max-gain control creation, EC gain get/set for both channels, I2S capture at 48 kHz 16/24-bit with expected BCLK, DAPM enable/disable commands, WoV enable/disable, hotword model upload with unchanged-hash short-circuit, EC/AP shared-memory paths, host-event-triggered audio capture, pointer monotonicity across ring wrap, no overrun logs under expected burst rates, and clean notifier unregister on removal.
