# subset-b-006353 ALSA PCM and OSS Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_oss.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/pcm_oss.c

## Purpose

`pcm_oss.c` implements ALSA PCM OSS emulation: the `/dev/dsp`-style character device, OSS ioctl surface, OSS-specific runtime parameter negotiation, read/write buffering, mmap behavior, procfs setup overrides, and registration hooks that attach OSS minors to ALSA PCM devices. It bridges legacy OSS applications onto ALSA `struct snd_pcm_substream` operations.

## Important APIs, Types, and Functions

The module exposes parameters `dsp_map`, `adsp_map`, and `nonblock_open`, registers `snd_pcm_oss_f_reg`, and installs `snd_pcm_oss_notify` with `snd_pcm_notify()`. `snd_pcm_oss_open()`, `snd_pcm_oss_release()`, `snd_pcm_oss_read()`, `snd_pcm_oss_write()`, `snd_pcm_oss_ioctl()`, `snd_pcm_oss_poll()`, and `snd_pcm_oss_mmap()` are the file operation entry points. Parameter helpers refine ALSA `snd_pcm_hw_params` to match OSS format/rate/channel/fragment requests. `snd_pcm_oss_change_params_locked()` is the main translation point from OSS runtime settings to ALSA `HW_PARAMS` and `SW_PARAMS`.

Data movement is split into byte-oriented OSS wrappers and frame-oriented ALSA helpers. `snd_pcm_oss_write1()` and `snd_pcm_oss_read1()` handle user buffers, partial fragments, signal interruption, nonblocking returns, and `runtime->oss.rw_ref`. `snd_pcm_oss_write2()` and `snd_pcm_oss_read2()` optionally pass through the OSS plugin chain. `snd_pcm_oss_write3()` and `snd_pcm_oss_read3()` call ALSA transfer helpers and recover from XRUN/suspend states.

## Control Flow

Open resolves the OSS minor to an ALSA PCM, applies per-task procfs setup overrides, waits for substreams unless nonblocking open is active, then opens playback and/or capture substreams. Initialization seeds OSS defaults such as 8 kHz mono, initial format by minor type, trigger enabled, and pending parameter setup. Reads, writes, ioctls, poll, and mmap force deferred parameter changes through `snd_pcm_oss_make_ready*()` before touching hardware state.

Ioctl dispatch implements classic OSS commands: reset/sync/post, speed, channels, format, fragment sizing, buffer-space queries, capabilities, trigger control, input/output pointer reporting, nonblocking mode, duplex checks, and mixer forwarding. Release syncs playback, drops capture, closes substreams, wakes open waiters, and releases module/card references.

## State and Persistence Behavior

Persistent state lives mostly in `runtime->oss`: pending params, selected rate/channels/format, period and buffer byte counts, trigger state, fragment/subdivision preferences, mmap size, software byte counters, partial-fragment buffer state, plugin list, and `params_lock`. Per-stream OSS setup lists persist under `pcm->streams[stream].oss.setup_list` and are edited through procfs when verbose procfs is enabled. Device registration state persists in `pcm->oss.reg` and `reg_mask`.

## Dependencies and Integration Points

This file depends on ALSA PCM core ioctls, `pcm_plugin.h`, OSS UAPI definitions from `linux/soundcard.h`, mixer OSS forwarding, ALSA proc/info APIs, card minor lookup, and the PCM notifier list in `pcm.c`. It integrates with plugin builders for format/rate/channel conversion when `CONFIG_SND_PCM_OSS_PLUGINS` is enabled.

## Risks and Edge Cases

The main risks are lock ordering around `params_lock`, mmap locks, and user copies; partial-fragment accounting; conversion between OSS bytes and ALSA frames when plugin sizes differ; nonblocking open/write behavior; and legacy apps that ignore errors. The mmap path intentionally uses trylock for parameter changes to avoid deadlock. Pointer and delay calculations include compatibility hacks such as `buggyptr`, capture overrun forwarding, and zeroing errors for broken `GETODELAY` consumers.

## Test Signals

Useful signals include opening `/dev/dsp` and `/dev/adsp` mappings, exercising `SNDCTL_DSP_*` ioctls, full-duplex and half-duplex open behavior, OSS mmap playback/capture, procfs setup overrides, nonblocking partial-fragment writes, XRUN recovery, and builds with and without `CONFIG_SND_PCM_OSS_PLUGINS`, `CONFIG_COMPAT`, `CONFIG_SND_VERBOSE_PROCFS`, and `CONFIG_SND_MIXER_OSS`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.c

## Purpose

`pcm_plugin.c` provides the shared OSS PCM plugin framework used by `pcm_oss.c` to adapt legacy OSS client streams to the actual ALSA hardware stream. It builds and runs ordered conversion chains for format conversion, mu-law conversion, channel routing, rate conversion, copy/deinterleave, and final I/O plugins.

## Important APIs, Types, and Functions

The key public helpers are `snd_pcm_plugin_build()`, `snd_pcm_plugin_free()`, `snd_pcm_plug_alloc()`, `snd_pcm_plug_client_size()`, `snd_pcm_plug_slave_size()`, `snd_pcm_plug_slave_format()`, `snd_pcm_plug_format_plugins()`, `snd_pcm_plug_client_channels_buf()`, `snd_pcm_plug_write_transfer()`, `snd_pcm_plug_read_transfer()`, `snd_pcm_area_silence()`, and `snd_pcm_area_copy()`. The framework operates on `struct snd_pcm_plugin` and `struct snd_pcm_plugin_channel` from `pcm_plugin.h`.

## Control Flow

`snd_pcm_plug_format_plugins()` compares client and slave formats, then appends plugins in the order needed for playback/capture: optional mu-law linearization, channel reduction, rate conversion through signed 16-bit, format conversion, channel extension, and interleaving conversion. `snd_pcm_plug_write_transfer()` walks the chain forward from `plugin_first`, allocating downstream channel buffers and invoking each plugin's `transfer()` callback. `snd_pcm_plug_read_transfer()` computes required source frames, then runs the same chain forward so captured driver data becomes OSS client data.

## State and Persistence Behavior

Plugin chain nodes are linked through `runtime->oss.plugin_first` and `plugin_last`. Each plugin owns optional scratch `buf`, `buf_frames`, `buf_channels`, private conversion data in `extra_data`, and an optional `private_free` callback. Scratch buffers are resized per period by `snd_pcm_plug_alloc()` and released through `snd_pcm_plugin_free()` when OSS params change or the substream closes.

## Dependencies and Integration Points

The framework depends on ALSA format helpers, OSS runtime plugin lists, and concrete plugin builders declared in `pcm_plugin.h`. `pcm_oss.c` decides when direct access is impossible, builds the chain, and calls transfer helpers during read/write.

## Risks and Edge Cases

Frame-count transforms must remain inverse enough for buffer sizing; a wrong `src_frames()` or `dst_frames()` result can underallocate scratch buffers or truncate audio. `snd_pcm_area_copy()` and `snd_pcm_area_silence()` assume byte-oriented areas except for special IMA ADPCM nibble handling. The framework caps plugin buffers at 1 MiB per period and rejects unsupported access patterns.

## Test Signals

Exercise OSS playback and capture where app format, hardware format, rate, channel count, and interleaving differ. Build coverage should include `CONFIG_SND_PCM_OSS_PLUGINS`; runtime coverage should confirm format fallback selection, mu-law conversion, noninterleaved hardware, and large-period rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.h -->
# sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.h

## Purpose

`pcm_plugin.h` defines the OSS PCM plugin interface shared by `pcm_oss.c` and the individual conversion plugins. It is the contract for plugin chain construction, frame-size conversion, channel-area layout, transfer callbacks, and fallback stubs when OSS plugins are disabled.

## Important APIs, Types, and Functions

Important types are `enum snd_pcm_plugin_action`, `struct snd_pcm_channel_area`, `struct snd_pcm_plugin_channel`, `struct snd_pcm_plugin_format`, and `struct snd_pcm_plugin`. The plugin object stores source/destination format triples, physical sample widths, access mode, frame-count callbacks, channel-buffer callback, transfer callback, action callback, list links, owning substream, optional private data, and scratch buffers.

Function declarations cover base plugin allocation/free, chain allocation, client/slave frame conversion, concrete builders for I/O, linear, mu-law, rate, route, and copy plugins, format-chain construction, transfer execution, client channel setup, and area copy/silence helpers. The header also exports OSS low-level read/write helpers used by plugin I/O nodes.

## Control Flow

Consumers build a chain by allocating concrete plugins with builder functions and linking them through `snd_pcm_plugin_append()` or insertion helpers in `pcm_oss.c`. During transfer, plugin callbacks consume arrays of `snd_pcm_plugin_channel` entries and optionally produce downstream channel arrays. `INIT` and `PREPARE` actions let stateful plugins reset conversion state before use.

## State and Persistence Behavior

The header does not store state directly, but it defines the state shape embedded in `runtime->oss` plugin lists. With `CONFIG_SND_PCM_OSS_PLUGINS` disabled, inline stubs make client/slave frame sizes identity mappings and return the requested format directly, so callers can compile without plugin conversion support.

## Dependencies and Integration Points

It depends on ALSA PCM types and is included by `pcm_oss.c`, `pcm_plugin.c`, `rate.c`, `route.c`, and other OSS plugin implementations. `FULL` and `HALF` expose route resolution constants from the wider OSS plugin subsystem.

## Risks and Edge Cases

The interface is sensitive to format width and channel count consistency. Plugins must honor channel `enabled`, `wanted`, `frames`, `area.first`, and `area.step`, or downstream code may copy invalid memory. Stub behavior when plugins are disabled means callers must still be able to operate in direct-compatible modes.

## Test Signals

Build both plugin-enabled and plugin-disabled configurations. Runtime validation should cover each concrete builder, `PREPARE` action reset behavior, channel-area interleaved and noninterleaved layouts, and OSS direct-mode fallback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/rate.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/rate.c

## Purpose

`rate.c` implements the OSS PCM rate-conversion plugin. It resamples signed 16-bit PCM between different source and destination rates using fixed-point linear interpolation, preserving per-channel history across transfer calls.

## Important APIs, Types, and Functions

`struct rate_priv` stores fixed-point `pitch`, current fractional `pos`, selected conversion function, cached frame-count mappings, and per-channel `last_S1`/`last_S2` samples. `snd_pcm_plugin_build_rate()` validates same channel count, S16 source and destination formats, and different rates, then installs `rate_transfer()`, `rate_src_frames()`, `rate_dst_frames()`, and `rate_action()`.

## Control Flow

The builder computes `pitch` in 11-bit fractional units and selects `resample_expand()` for upsampling or `resample_shrink()` for downsampling. `rate_transfer()` computes destination frames, clamps to destination capacity, and calls the selected resampler. The resamplers walk each channel, skip disabled inputs with optional silence output, interpolate between saved samples, update destination samples, and persist the final interpolation position and sample history.

## State and Persistence Behavior

Conversion state is per plugin instance and persists in `plugin->extra_data`. `rate_init()` resets position and channel sample history on `INIT` and `PREPARE`. `old_src_frames` and `old_dst_frames` cache recent frame-size calculations to stabilize reciprocal sizing in the plugin chain.

## Dependencies and Integration Points

The rate plugin depends on `pcm_plugin.h`, ALSA format assumptions, and `snd_pcm_area_silence()` for disabled channels. It is inserted by `snd_pcm_plug_format_plugins()` when client and slave rates differ by more than the framework's tolerance and the stream has been converted to signed 16-bit samples.

## Risks and Edge Cases

The converter is deliberately basic, not high-quality audio resampling. It assumes byte-aligned S16 channel areas and matching channel counts. Bad frame-count calculations can create buffer underruns in the chain. Fractional position and saved samples must reset on prepare to avoid carrying old audio across stream restarts.

## Test Signals

Test OSS playback/capture at rates that require upsampling and downsampling, including multi-channel streams, disabled-channel paths, repeated prepare/start cycles, and small period sizes that stress frame-count rounding.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/route.c -->
# sources/distributed-fs/ceph-client/sound/core/oss/route.c

## Purpose

`route.c` implements the OSS PCM channel-routing plugin. It adapts channel counts when sample format and rate already match, supporting mono expansion, channel reduction, direct channel copies, and silence for missing destination channels.

## Important APIs, Types, and Functions

The exported builder is `snd_pcm_plugin_build_route()`. It validates identical source/destination rate and format, creates a plugin named `route conversion`, and installs `route_transfer()`. Internal helpers `zero_areas()` and `copy_area()` silence or copy `struct snd_pcm_plugin_channel` areas.

## Control Flow

`route_transfer()` clamps frames to destination channel capacity. If there is one source channel, it copies that channel into every destination. Otherwise it copies matching source-to-destination channels until either side ends, then silences remaining wanted destination channels. The plugin returns the number of destination frames processed.

## State and Persistence Behavior

The route plugin is stateless after construction; all behavior derives from plugin source/destination channel counts and per-transfer channel arrays. Destination channel `enabled` flags are updated on each call.

## Dependencies and Integration Points

It depends on `pcm_plugin.h`, `snd_pcm_area_copy()`, and `snd_pcm_area_silence()`. `pcm_plugin.c` inserts it before rate conversion for channel reduction and after format/rate conversion for channel extension.

## Risks and Edge Cases

The route policy is simple duplication/truncation rather than a mixing matrix. Multi-channel downmix does not combine channels; it drops channels beyond destination count. Missing destinations are silenced only when `wanted` is set, so callers must populate channel metadata correctly.

## Test Signals

Exercise mono-to-stereo expansion, stereo-to-mono reduction, multichannel truncation, capture and playback directions, disabled destination channels, and format/rate mismatch rejection in the builder.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/oss/route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm.c

## Purpose

`pcm.c` is the ALSA midlevel PCM registry and lifecycle implementation. It creates PCM devices and streams, manages substreams and runtime allocation, exposes control ioctls for PCM enumeration/info, registers device nodes and procfs/sysfs entries, handles disconnect/suspend teardown, and provides the OSS notifier hook used by `pcm_oss.c`.

## Important APIs, Types, and Functions

Public APIs include `snd_pcm_format_name()`, `snd_pcm_new_stream()`, `snd_pcm_new()`, `snd_pcm_new_internal()`, `snd_pcm_attach_substream()`, `snd_pcm_detach_substream()`, and `snd_pcm_notify()`. Global state includes `snd_pcm_devices`, `register_mutex`, and, when OSS is enabled, `snd_pcm_notify_list`. Device callbacks are `snd_pcm_dev_register()`, `snd_pcm_dev_disconnect()`, and `snd_pcm_dev_free()`.

## Control Flow

PCM creation allocates a `struct snd_pcm`, initializes locks and wait queues, creates playback and capture streams, and registers an ALSA device object. Stream creation allocates stream devices, procfs roots, substream objects, self groups, and mmap counters. Registration inserts the PCM in sorted global order, registers playback/capture device nodes, initializes timers, and calls OSS notifiers. Opening a substream selects an available or preferred subdevice, handles half-duplex exclusion, allocates runtime/status/control pages, initializes wait queues and buffer locks, sets state to OPEN, stores the current PID, and returns the substream.

Disconnect removes the PCM from the global list, wakes waiters, marks live runtimes DISCONNECTED, stops running streams, sync-stops substreams, notifies OSS, unregisters devices, and removes channel maps. Freeing invokes unregister notifiers, private cleanup, preallocation cleanup, stream/substream freeing, and PCM object free.

## State and Persistence Behavior

Persistent PCM state includes the global device list, each PCM's streams, substreams, open counts, proc roots, sysfs devices, channel-map controls, and runtime objects while open. Runtime status/control pages are separately allocated to support mmap-visible state. OSS setup lists are stream-persistent when OSS support is built in.

## Dependencies and Integration Points

This file depends on ALSA card/device/control/timer/info core, PCM native file ops, procfs, sysfs device registration, PM callbacks, and optional OSS notification. User control ioctls call into `snd_pcm_info_user()`, while PCM device nodes use file ops declared elsewhere.

## Risks and Edge Cases

Registration and disconnect are lock-sensitive because the global PCM list, open waiters, device nodes, and runtime state can change concurrently. Preferred subdevice and `O_APPEND` reopen semantics are subtle. Runtime detach must avoid timer races by clearing `substream->runtime` under timer lock when needed. Missing notifier cleanup can leave stale OSS minors.

## Test Signals

Validate PCM enumeration via control ioctls, playback/capture device registration, substream open/close, preferred subdevice behavior, half-duplex exclusion, suspend/disconnect while open, procfs status files, sysfs `pcm_class`, and OSS notifier registration/unregistration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_compat.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_compat.c

## Purpose

`pcm_compat.c` is included by `pcm_native.c` to implement 32-bit and x32 compatibility wrappers for ALSA PCM ioctls on 64-bit kernels. It translates structure layouts, pointer arrays, frame counters, mmap sync records, status records, and boundary values between compat userspace and native kernel PCM APIs.

## Important APIs, Types, and Functions

Important wrappers include `snd_pcm_ioctl_hw_params_compat()`, `snd_pcm_ioctl_sw_params_compat()`, `snd_pcm_ioctl_channel_info_compat()`, `snd_pcm_status_user_compat64()`, `snd_pcm_ioctl_xferi_compat()`, `snd_pcm_ioctl_xfern_compat()`, `snd_pcm_ioctl_sync_ptr_x32()`, `snd_pcm_ioctl_sync_ptr_buggy()`, and the main dispatcher `snd_pcm_ioctl_compat()`. Compat structs mirror 32-bit versions of hw/sw params, channel info, transfer descriptors, x32 mmap sync records, and historical buggy sync layouts.

## Control Flow

The dispatcher retrieves `struct snd_pcm_file`, disables compat mmap of old status/control records, then either forwards layout-compatible commands to `snd_pcm_common_ioctl()` or handles translated commands locally. HW refine/params copies a 32-bit params block into a native object, calls native refine/params, copies results back, and recalculates runtime boundary after real params. Transfer wrappers read compat user pointers, call native `snd_pcm_lib_read/write` or vector variants, then write the result field back.

## State and Persistence Behavior

Most functions are translation-only. Persistent effects are native PCM effects: hardware/software parameter changes, appl pointer updates, DMA sync, rewind/forward, stream state changes, and `pcm_file->no_compat_mmap = 1`. Boundary recalculation updates `runtime->boundary` after compat HW params.

## Dependencies and Integration Points

The file depends on Linux compat helpers, native PCM APIs from `pcm_native.c`, runtime mmap status/control structures, stream locks, DMA buffer sync, and x86 x32 ABI conditionals. It is not a standalone compilation unit; it is included into the native PCM implementation.

## Risks and Edge Cases

Layout mistakes are ABI regressions. Pointer-array transfer copies up to 128 channel pointers and rejects larger channel counts. Sync pointer handling includes a compatibility path for a historical 32-bit layout bug, and x32 has a distinct structure despite running on 64-bit kernels. Boundary conversion must keep 32-bit userspace ring pointers coherent with native wider boundaries.

## Test Signals

Run 32-bit ALSA PCM applications on a 64-bit kernel, including hw refine/params, sw params, mmap sync, status ext, interleaved and noninterleaved transfers, rewind/forward/delay, x32-specific tests where available, and regression tests for old libasound sync-pointer behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_dmaengine.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_dmaengine.c

## Purpose

`pcm_dmaengine.c` provides reusable ALSA PCM helper APIs for drivers that move audio with Linux dmaengine cyclic DMA. It converts PCM params to DMA slave config, opens/closes DMA-backed substreams, implements common trigger and pointer callbacks, requests channels, synchronizes stop, and refines hardware capabilities from DMA channel caps.

## Important APIs, Types, and Functions

`struct dmaengine_pcm_runtime_data` stores the channel, submitted cookie, and fallback period-completion position. Exported APIs include `snd_dmaengine_pcm_get_chan()`, `snd_hwparams_to_dma_slave_config()`, `snd_dmaengine_pcm_set_config_from_dai_data()`, `snd_dmaengine_pcm_trigger()`, `snd_dmaengine_pcm_pointer_no_residue()`, `snd_dmaengine_pcm_pointer()`, `snd_dmaengine_pcm_request_channel()`, `snd_dmaengine_pcm_open()`, `snd_dmaengine_pcm_sync_stop()`, `snd_dmaengine_pcm_close()`, `snd_dmaengine_pcm_close_release_chan()`, and `snd_dmaengine_pcm_refine_runtime_hwparams()`.

## Control Flow

Open validates a DMA channel, constrains periods to integers, allocates runtime private data, and stores the channel. START prepares a cyclic descriptor over the runtime DMA buffer, sets period interrupt callback unless no-period-wakeup is active, submits it, and issues pending DMA. Pause/resume/suspend/stop map to dmaengine pause, resume, terminate, or synchronize behavior. Pointer reads DMA residue and in-flight bytes to compute current frame position and runtime delay.

## State and Persistence Behavior

Per-open state persists in `runtime->private_data`. DMA state persists in the dmaengine channel after START via the submitted cookie. `prtd->pos` is a software fallback advanced by period callbacks and used by deprecated no-residue pointer reporting. Close synchronizes the channel, optionally releases it, and frees private data.

## Dependencies and Integration Points

The file depends on Linux dmaengine, ALSA PCM core, ASoC DAI DMA data structures, `sound/dmaengine_pcm.h`, and PCM buffer helpers. ASoC and platform PCM drivers commonly wire these exported helpers into their `open`, `close`, `trigger`, `pointer`, and hw-param paths.

## Risks and Edge Cases

DMA residue reporting varies by controller; unsupported or coarse residue granularity can produce imprecise pointers and sets `SNDRV_PCM_INFO_BATCH`. START must not submit descriptors with invalid buffer or period sizes. Pause-on-suspend only works when runtime info advertises pause support. `runtime->private_data` ownership means drivers cannot use that field for other state when using this helper.

## Test Signals

Validate playback and capture on dmaengine-backed drivers, pause/resume, suspend, stop synchronization, cyclic period interrupts, no-period-wakeup mode, pointer accuracy under residue and no-residue paths, DMA capability-derived format masks, and channel release on close.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_dmaengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_drm_eld.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_drm_eld.c

## Purpose

`pcm_drm_eld.c` contains ALSA helpers for HDMI/DisplayPort ELD data. It parses DRM ELD blobs into `snd_parsed_hdmi_eld`, constrains PCM hardware rates/channels based on sink Short Audio Descriptors, and prints ELD information for debug and procfs output.

## Important APIs, Types, and Functions

Exported APIs are `snd_pcm_hw_constraint_eld()`, `snd_parse_eld()`, `snd_show_eld()`, and, under procfs, `snd_print_eld_info()`. Internal helpers include `sad_rate_mask()`, `sad_max_channels()`, `eld_limit_rates()`, `eld_limit_channels()`, `hdmi_update_short_audio_desc()`, and multiple printing helpers for rates, sample bits, speaker allocation, and SAD fields.

## Control Flow

`snd_pcm_hw_constraint_eld()` adds reciprocal hw-rules: rate constraints depend on requested channels, and channel constraints depend on requested rate. The rules walk the ELD SAD list and derive allowed rate masks and maximum channels. `snd_parse_eld()` validates ELD version, baseline length, monitor-name length, SAD bounds, then extracts monitor identity, connection type, speaker allocation, port ID, manufacturer/product IDs, and all SADs. Debug/proc print paths format the parsed structure into human-readable output.

## State and Persistence Behavior

This file does not own long-lived global state. Parsed ELD persists in caller-provided `struct snd_parsed_hdmi_eld`; hw constraints store the caller's ELD pointer as rule private data in the PCM runtime. If speaker allocation is absent but SADs exist, parsing defaults `spk_alloc` to all speakers to avoid over-restricting playback.

## Dependencies and Integration Points

Dependencies include DRM EDID/ELD helpers, HDMI coding constants, ALSA PCM hw-rule APIs, ALSA info buffers, unaligned access helpers, and device logging. HDMI/DP audio drivers use these helpers to limit PCM params to sink capabilities and expose connector audio information.

## Risks and Edge Cases

ELD buffers can be malformed, so bounds checks on monitor names and SAD entries are critical. Compressed formats map channel/rate capabilities differently from LPCM, and unsupported coding types fall back to generic masks. Constraint logic must consider both rate and channel intervals or it can reject valid modes or allow unsupported sink combinations.

## Test Signals

Test valid and malformed ELD blobs, HDMI and DisplayPort connection types, LPCM and compressed SADs, no speaker-allocation fallback, hw-param refinement for rate/channel combinations, debug output, and procfs ELD formatting when `CONFIG_SND_PROC_FS` is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_drm_eld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_iec958.c -->
# sources/distributed-fs/ceph-client/sound/core/pcm_iec958.c

## Purpose

`pcm_iec958.c` creates and fills consumer IEC958/S/PDIF channel-status bytes from ALSA PCM runtime or hardware parameters. It gives drivers a small helper layer for default status generation plus rate and word-length completion.

## Important APIs, Types, and Functions

Exported functions are `snd_pcm_create_iec958_consumer_default()`, `snd_pcm_fill_iec958_consumer()`, `snd_pcm_fill_iec958_consumer_hw_params()`, `snd_pcm_create_iec958_consumer()`, and `snd_pcm_create_iec958_consumer_hw_params()`. `fill_iec958_consumer()` maps PCM rates and sample widths into IEC958 AES status bits when the caller left those fields unspecified.

## Control Flow

Default creation validates a minimum four-byte buffer, clears it, and fills consumer, no-copyright, no-emphasis, general category, unspecified source/channel, 1000 ppm clock, and unknown sample-rate/word-length markers. Fill helpers then replace the unspecified sample-rate field for supported rates from 32 kHz through 192 kHz and optionally replace byte-four word-length bits for 16, 18, 20, 24, or 32-bit PCM. Create helpers perform default creation followed by fill.

## State and Persistence Behavior

All state is caller-owned in the `u8 *cs` channel-status buffer. The helpers intentionally preserve fields already specified by the caller and only fill `NOTID` rate or word-length values. There is no global or runtime-persistent state.

## Dependencies and Integration Points

The file depends on IEC958 AES bit definitions, ALSA PCM runtime/hw-param helpers, and exported kernel symbols for use by PCM and digital audio drivers. Runtime variants read `runtime->rate` and `runtime->format`; hw-param variants read `params_rate()` and `params_width()`.

## Risks and Edge Cases

Buffers shorter than four bytes are invalid, and word-length filling only occurs when a fifth byte is present. Unsupported rates or widths return `-EINVAL`. The helper treats 32-bit samples as 24-bit IEC958 word length, matching common S/PDIF packing assumptions.

## Test Signals

Validate default buffer contents, fill behavior for each supported sample rate and width, preservation of prefilled status bits, short-buffer rejection, unsupported rate/width rejection, and use from both runtime and hw-param based driver paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/pcm_iec958.c -->
