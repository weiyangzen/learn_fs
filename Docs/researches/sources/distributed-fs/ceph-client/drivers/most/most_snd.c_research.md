# sources/distributed-fs/ceph-client/drivers/most/most_snd.c

## Purpose

`most_snd.c` is the ALSA-facing component for the MOST core. It exposes MOST synchronous audio channels as ALSA PCM playback or capture devices, translates ALSA ring-buffer traffic to and from MOST buffer objects (`struct mbo`), and registers itself as a `struct most_component` named `"sound"`. The driver is not a hardware driver by itself; it depends on a MOST hardware dependent module, such as the USB HDM, to provide `most_interface` channels and MBO transport.

## Important APIs, Types, and Functions

The central per-channel state is `struct channel`: it binds an ALSA `snd_pcm_substream`, channel hardware constraints, the `most_interface`, `most_channel_config`, ALSA card, channel id, ring positions, stream-running state, a playback kthread, a waitqueue, and a selected endian/width copy function. `struct sound_adapter` groups all audio channels belonging to one MOST interface under a single ALSA card and tracks whether the card has been registered.

Key ALSA callbacks are `pcm_open`, `pcm_close`, `pcm_prepare`, `pcm_trigger`, and `pcm_pointer`, collected in `pcm_ops`. MOST component callbacks are `audio_probe_channel`, `audio_disconnect_channel`, `audio_rx_completion`, `audio_tx_completion`, and `audio_create_sound_card`, collected in `comp`. `audio_init` registers the component and configfs subsystem; `audio_exit` unregisters both.

Data conversion helpers are `swap_copy16`, `swap_copy24`, `swap_copy32`, and directional wrappers such as `alsa_to_most_copy16` and `most_to_alsa_copy32`. `copy_data` is the shared transfer primitive; it copies between `runtime->dma_area` and `mbo->virt_address`, handles ring wrap, advances `buffer_pos` and `period_pos`, and returns whether ALSA should be notified via `snd_pcm_period_elapsed`.

## Control Flow

Channel creation begins when MOST core calls `audio_probe_channel`. The function rejects non-synchronous channels, parses the configfs argument string as `<channels>x<sample-resolution>`, locates or allocates a `sound_adapter`, allocates a `channel`, calculates ALSA hardware constraints with `audio_set_hw_params`, creates one PCM device with either playback or capture stream count, installs `pcm_ops`, and assigns vmalloc-managed PCM buffers.

After all requested channels are configured, `audio_create_sound_card` registers the first unregistered adapter card. Opening a PCM stream stores the substream, starts a playback kthread for TX, and calls `most_start_channel`. Preparing the stream selects the copy function based on direction, sample width, and endian format, then resets the ring cursors. Trigger start flips `is_stream_running` and wakes the TX kthread; trigger stop clears it.

TX data flow is thread-driven. `playback_thread` waits until the stream is running and `most_get_mbo` returns a free MBO, then copies ALSA frames into the MBO and submits it with `most_submit_mbo`; MOST TX completion only wakes the waitqueue. RX data flow is completion-driven: `audio_rx_completion` finds the channel, copies received MBO data into the ALSA ring if the stream is running, returns the MBO with `most_put_mbo`, and notifies ALSA on period boundaries.

## State and Persistence Behavior

All state is runtime kernel state. There is no on-disk persistence. Adapter membership is kept in the global `adpt_list`; `iface->priv` points at the adapter. Per-channel ring state is `period_pos`, `buffer_pos`, and `is_stream_running`. ALSA card and PCM device lifetimes are tied to probe/disconnect and adapter release. The code assumes channel configuration remains valid for the channel lifetime because `struct channel` stores the `cfg` pointer from MOST core.

The playback kthread is created on open and stopped on close for TX channels. Capture channels do not create a worker thread. Disconnect removes the channel and releases the whole adapter/card once the last channel is gone.

## Dependencies and Integration Points

This file integrates three subsystems: ALSA PCM (`sound/core.h`, `sound/pcm.h`, `sound/pcm_params.h`), MOST core (`linux/most.h`), and kernel threading/waitqueues. It expects a MOST HDM to provide synchronous channels with `subbuffer_size`, `buffer_size`, `num_buffers`, and direction. Configfs integration comes from `most_register_configfs_subsys(&comp)`, and the user-provided PCM format string is passed through the MOST config path.

The ALSA hardware model is fixed to 48 kHz, interleaved, block-transfer, mmap-capable PCM. Supported sample widths are 8, 16, packed 24, and 32 bits; for little-endian formats wider than 8 bits the driver swaps byte order when moving between ALSA and MOST.

## Risks and Edge Cases

`copy_data` relies on `cfg->subbuffer_size` as the ALSA frame byte count; a zero or inconsistent subbuffer size would break frame math, although `audio_set_hw_params` catches mismatch between channel count, sample width, and subbuffer size. The global adapter list and per-channel fields are not guarded by an explicit lock in this file, so it relies on MOST/ALSA lifecycle serialization. Stream-running state is a plain boolean shared by ALSA callbacks, completion context, and the playback thread; races are mitigated by simple idempotent behavior but not strongly synchronized.

`audio_probe_channel` releases the whole adapter on several channel-local allocation failures, which is correct for newly allocated adapters but can be hazardous if later channel probing fails after earlier channels were added to the same unregistered adapter. The driver only supports one registration pass per adapter: if `adpt->registered` is already true, probing another channel returns `-ENOSPC`.

## Test Signals

Build signals are `CONFIG_MOST` plus ALSA support and this component being compiled. Runtime signals include successful component/configfs registration, ALSA card creation named `Microchip INIC`, PCM open/prepare/trigger cycles, and absence of `most_start_channel()` or PCM format errors. Functional tests should cover TX and RX at 48 kHz for all supported widths, ring wrap across `runtime->buffer_size`, period notifications, open/close cleanup, device disconnect while idle, and behavior when MOST completions arrive while the stream is stopped.
