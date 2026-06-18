# Research: subset-b-006568

Grouped research for the exact subset-b-006568 source list. Each section preserves the source path in its title and is wrapped for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.c

## Purpose
Implements VirtIO sound PCM discovery and ALSA PCM device construction. It converts VirtIO stream descriptors into `snd_pcm_hardware`, groups substreams by function node id, builds ALSA PCM devices, and handles asynchronous VirtIO PCM events.

## Important APIs, Types, And Functions
- Module parameters `pcm_buffer_ms`, `pcm_periods_min`, `pcm_periods_max`, `pcm_period_ms_min`, and `pcm_period_ms_max` bound derived ALSA hardware limits.
- `g_v2a_format_map` and `g_v2a_rate_map` translate VirtIO PCM format/rate bits into ALSA format masks and rate ranges.
- `virtsnd_pcm_build_hw()` validates channel/rate/format data and computes `buffer_bytes_max`, `period_bytes_min`, and `period_bytes_max`.
- `virtsnd_pcm_find()` and `virtsnd_pcm_find_or_create()` manage `snd->pcm_list` entries keyed by VirtIO function node id.
- `virtsnd_pcm_validate()` rejects invalid module parameter combinations before the device starts.
- `virtsnd_pcm_parse_cfg()` queries `VIRTIO_SND_R_PCM_INFO`, initializes every `virtio_pcm_substream`, and counts stream directions per PCM node.
- `virtsnd_pcm_build_devs()` creates `snd_pcm` devices, attaches kernel substreams back to VirtIO substream records, sets ops, and installs vmalloc managed buffers.
- `virtsnd_pcm_event()` handles VirtIO PCM events, currently marking xruns under the substream lock.

## Control Flow
Initialization first calls validation, then `virtsnd_pcm_parse_cfg()` reads the VirtIO config stream count, preinitializes substream synchronization fields, fetches all stream info through the control queue, converts each stream to ALSA hardware constraints, and increments playback/capture counts. `virtsnd_pcm_build_devs()` then makes an ALSA PCM per node, allocates per-direction substream pointer arrays, binds ALSA substream numbers to `virtio_pcm_substream` entries, and registers `virtsnd_pcm_ops` for playback/capture.

## State And Persistence
Persistent runtime state lives in devm-managed `snd->substreams`, `snd->pcm_list`, and per-substream fields such as `hw`, `features`, `direction`, `buffer_bytes`, `hw_ptr`, `xfer_enabled`, `xfer_xrun`, and wait/work structures. There is no disk persistence. Device lifetime relies on the parent `virtio_snd` and ALSA card lifetime; module parameters persist only as loaded module settings.

## Dependencies And Integration Points
This file depends on Linux VirtIO config access, ALSA PCM core, `virtio_card.h`, and the VirtIO sound UAPI structures. It integrates with `virtio_pcm_ops.c` through `virtsnd_pcm_ops`, with `virtio_pcm_msg.c` through substream message fields, and with `virtio_ctl_msg` query/send helpers.

## Risks
- Hardware limits are derived using integer math on milliseconds and rates; unusual low rates or formats can expose zero/minimum period edge cases.
- Unsupported VirtIO formats/rates are ignored; a device advertising only unsupported bits fails initialization.
- `VIRTIO_SND_EVT_PCM_PERIOD_ELAPSED` is not implemented for shared-memory elapsed reporting, so message completion remains the main period signal.
- `virtsnd_pcm_build_devs()` assumes ALSA substream numbering matches the populated `vs->substreams` order.

## Test Signals
Useful signals include boot/probe with multiple playback and capture streams under one node, invalid module parameter rejection, ALSA `aplay`/`arecord` with several formats/rates, xruns from the device, and teardown/reprobe under module unload. Kernel logs for "invalid channel range", "no supported PCM sample formats", and "snd_pcm_new failed" are direct failure indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.h -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.h

## Purpose
Declares the VirtIO PCM data model and cross-file PCM APIs used by the VirtIO sound driver. It is the contract between PCM discovery, PCM ALSA ops, and PCM message transport.

## Important APIs, Types, And Functions
- `struct virtio_pcm_substream` stores device identity, ALSA substream linkage, hardware constraints, indirect PCM state, transfer flags, message arrays, pending count, and synchronization objects.
- `struct virtio_pcm_stream` groups playback or capture substreams plus channel maps.
- `struct virtio_pcm` represents one ALSA PCM device keyed by VirtIO node id.
- Exports `virtsnd_pcm_validate()`, `virtsnd_pcm_parse_cfg()`, `virtsnd_pcm_build_devs()`, `virtsnd_pcm_event()`, notify callbacks, lookup helpers, control-message allocation, and I/O message lifecycle helpers.

## Control Flow
The header has no runtime flow, but it defines how the driver flows: parse config into `virtio_pcm_substream`, build `virtio_pcm` devices, use ALSA callbacks from `virtsnd_pcm_ops`, then send/complete transport messages through the queue notify callbacks.

## State And Persistence
The key mutable state is per-substream. `lock` protects IRQ/operator shared fields, `msg_empty` synchronizes stop/release draining, `elapsed_period` defers ALSA period notification to process context, and `msg_count` tracks device-owned messages. Nothing is persisted outside kernel memory.

## Dependencies And Integration Points
Includes Linux atomic and VirtIO config headers plus ALSA PCM and indirect PCM headers. It references `virtio_snd` from `virtio_card.h` indirectly through source inclusions and exposes function signatures consumed by `virtio_card.c`, `virtio_pcm.c`, `virtio_pcm_msg.c`, and `virtio_pcm_ops.c`.

## Risks
The structure fields encode concurrency assumptions. Misusing `msg_count`, `xfer_enabled`, or `stopped` without the documented lock/wait discipline can lead to use-after-free or stale device-owned messages.

## Test Signals
Compile coverage is important because this header couples multiple translation units. Runtime tests should exercise open/close, hw_params/hw_free, start/stop, suspend/resume, and interrupt completion paths that mutate the declared state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_msg.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_msg.c

## Purpose
Implements VirtIO PCM period I/O message allocation, scatter-gather construction, queue submission, completion handling, and queue notify callbacks. It turns vmalloc-backed ALSA PCM buffers into VirtIO messages.

## Important APIs, Types, And Functions
- `struct virtio_pcm_msg` wraps a `virtio_snd_pcm_xfer` request, a `virtio_snd_pcm_status` response, payload length, and flexible SG array.
- `virtsnd_pcm_sg_num()` and `virtsnd_pcm_sg_from()` compute and populate physically contiguous SG segments for vmalloc memory.
- `virtsnd_pcm_msg_alloc()` creates one message per ALSA period, with xfer/status/data SG entries.
- `virtsnd_pcm_msg_send()` accumulates updated bytes by period and enqueues complete-period messages to the TX or RX virtqueue.
- `virtsnd_pcm_msg_complete()` advances `hw_ptr`, updates runtime delay from device latency, schedules period work, and wakes stop waiters when drained.
- `virtsnd_pcm_tx_notify_cb()` and `virtsnd_pcm_rx_notify_cb()` dispatch queue completions.
- `virtsnd_pcm_ctl_msg_alloc()` builds PCM control messages with the stream id set.

## Control Flow
`hw_params` allocates messages per period. Playback/capture ack paths call `virtsnd_pcm_msg_send()` with changed ring-buffer ranges while queue and substream locks are held. When enough bytes fill a period, the message is submitted with request/data/status SG ordering appropriate for playback or capture. Virtqueue interrupts run `virtsnd_pcm_notify_cb()`, drain completed buffers with callbacks disabled/enabled safely, and call `virtsnd_pcm_msg_complete()`.

## State And Persistence
Each message tracks `length`, which is reset on completion. `vss->msg_count` counts in-flight messages; `vss->hw_ptr` is advanced modulo `buffer_bytes`; `runtime->delay` stores backend latency in frames. `msg_empty` is signaled when transfer is disabled and all messages are complete. State is transient and tied to ALSA hw_params/hw_free lifetime.

## Dependencies And Integration Points
Uses ALSA `pcm_params`, Linux scatterlist/vmalloc/page helpers, VirtIO virtqueues, and `virtio_ctl_msg` helpers. It expects lock ordering from `virtio_pcm_ops.c`: queue lock plus substream lock for submissions, queue lock in notify path, and substream lock for mutable transfer state.

## Risks
- `virtsnd_pcm_sg_num()` assumes `vmalloc_to_page()` succeeds for the DMA area.
- Message freeing is unsafe unless the queue is drained; this is handled by ops but is a central lifetime risk.
- `offset + bytes - 1` assumes nonzero `bytes`.
- Capture completion tolerates short/invalid status by advancing by message length; this avoids stalls but can hide backend bugs.
- Queue notification is skipped for devices using message polling; tests need both feature states.

## Test Signals
Use playback and capture with vmalloc buffers spanning multiple pages, periods smaller/larger than page fragments, stop with pending messages, timeout during release, polling-feature devices, and backend-provided `latency_bytes`. Look for period callbacks, pointer movement, and absence of use-after-free on rapid open/hw_params/hw_free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_ops.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_ops.c

## Purpose
Provides ALSA PCM operations for VirtIO sound playback and capture. It negotiates parameters with the device, allocates I/O messages, starts/stops streams, exposes hardware pointers, and bridges ALSA indirect transfer callbacks to VirtIO period messages.

## Important APIs, Types, And Functions
- `g_a2v_format_map` and `g_a2v_rate_map` translate ALSA selections to VirtIO protocol values.
- `virtsnd_pcm_open()` installs hardware constraints and synchronously releases stale queue state.
- `virtsnd_pcm_dev_set_params()` sends `VIRTIO_SND_R_PCM_SET_PARAMS` with selected buffer/period/channel/format/rate and negotiated feature bits.
- `virtsnd_pcm_hw_params()` rejects non-drained queues, sets device params, frees old messages, and allocates new per-period messages.
- `virtsnd_pcm_prepare()` resets local transfer state or reprograms the device after suspend, initializes indirect PCM state, and sends PREPARE.
- `virtsnd_pcm_trigger()` handles START/STOP/PAUSE/SUSPEND commands and sends VirtIO START/STOP control messages.
- `virtsnd_pcm_sync_stop()` sends RELEASE and waits for `msg_empty` so device-owned messages can be freed safely.
- Playback/capture `pointer` and `ack` callbacks use `snd_pcm_indirect_*` helpers.

## Control Flow
Open loads `runtime->hw`, marks whether old messages are pending, and calls sync stop. `hw_params` sends backend params and prepares messages. `prepare` resets buffer pointer state and sends PREPARE. On START, capture prequeues the whole buffer, enables transfer under locks, then sends START. Playback sends messages from `ack` as userspace writes into periods. STOP/PAUSE/SUSPEND disable transfer and send STOP; later `sync_stop` RELEASEs the stream and waits for queue drain.

## State And Persistence
Mutable per-stream state includes `stopped`, `suspended`, `xfer_enabled`, `xfer_xrun`, `msg_count`, `buffer_bytes`, `hw_ptr`, and `pcm_indirect`. The most important persistence behavior is not disk persistence but device ownership: messages may remain owned by the backend after stop until RELEASE completion drains them.

## Dependencies And Integration Points
Depends on ALSA PCM and indirect PCM helpers, `virtio_pcm_msg.c` for message send/free/pending, and VirtIO control messages. It is exported as `virtsnd_pcm_ops[]` for playback and capture in `virtio_pcm.c`.

## Risks
- START enables `xfer_enabled` before the START control message returns; failure paths only clear it for allocation failure, so backend START errors should be scrutinized.
- `sync_stop` may timeout or be interrupted, leaving messages allocated until a later safe cleanup point.
- Capture prequeues the full buffer at start, so buffer size and period configuration directly affect initial queue pressure.
- Suspend path relies on reprogramming params in `prepare`; coverage must include suspend/resume with pending streams.

## Test Signals
Test ALSA open/close, repeated hw_params without hw_free, rapid stop/start, pause/release, suspend/resume, release timeout, capture start prequeue, playback ack-driven queuing, and xrun/error injection. `msg_count` reaching zero after RELEASE is the key safety signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/Kconfig -->
# sources/distributed-fs/ceph-client/sound/x86/Kconfig

## Purpose
Defines the x86-specific sound driver menu and the Intel HDMI LPE audio config option.

## Important APIs, Types, And Functions
- `menuconfig SND_X86` gates x86 sound devices that are not SoC or PCI class drivers.
- `config HDMI_LPE_AUDIO` builds the Intel Atom HDMI audio without HDAudio support as a tristate.

## Control Flow
Kconfig selection enables compilation only on `X86`. `HDMI_LPE_AUDIO` depends on `DRM_I915` and selects `SND_PCM`, linking the audio driver to i915-provided platform device support.

## State And Persistence
The selected Kconfig symbols persist in kernel build configuration and determine whether the module or built-in object is produced.

## Dependencies And Integration Points
Integrates with `sound/x86/Makefile`, ALSA PCM, and i915's HDMI LPE platform-data bridge.

## Risks
Because `HDMI_LPE_AUDIO` depends directly on `DRM_I915`, build coverage must include i915 configurations. Missing `SND_PCM` would break ALSA symbols, hence the explicit select.

## Test Signals
Check `oldconfig` visibility on x86, module build for `CONFIG_HDMI_LPE_AUDIO=m`, and built-in build for `=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/Makefile -->
# sources/distributed-fs/ceph-client/sound/x86/Makefile

## Purpose
Builds the Intel HDMI LPE ALSA module/object for `CONFIG_HDMI_LPE_AUDIO`.

## Important APIs, Types, And Functions
- `snd-hdmi-lpe-audio-y += intel_hdmi_audio.o` defines the composite module contents.
- `obj-$(CONFIG_HDMI_LPE_AUDIO) += snd-hdmi-lpe-audio.o` hooks the object into Kbuild.

## Control Flow
Kbuild includes `intel_hdmi_audio.o` when the Kconfig symbol is enabled, producing either a module or built-in object according to the tristate value.

## State And Persistence
No runtime state. Build outputs are controlled by kernel configuration.

## Dependencies And Integration Points
Consumes the Kconfig symbol from `sound/x86/Kconfig` and compiles the driver that binds the `hdmi-lpe-audio` platform device.

## Risks
Any additional x86 sound source files must be added to the appropriate composite object; otherwise Kbuild will not link them.

## Test Signals
Run kernel `make M=sound/x86` or full build with `CONFIG_HDMI_LPE_AUDIO=m/y` and verify `snd-hdmi-lpe-audio` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.c -->
# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.c

## Purpose
Implements the Intel HDMI/DP LPE ALSA platform driver used on Atom platforms without HDAudio. It binds to an i915-created platform device, creates ALSA playback PCM devices, programs HDMI/DP audio registers, handles display hotplug/ELD changes, and advances a fixed hardware buffer descriptor ring.

## Important APIs, Types, And Functions
- Module parameters `index`, `id`, and `single_port` control ALSA card identity and legacy port mapping.
- `had_pcm_hardware` advertises playback formats, rates, channel counts, period constraints, and buffer limits.
- Register helpers `had_read_register*()`, `had_write_register*()`, and `had_enable_audio()` centralize MMIO access and preserve cached `AUD_CONFIG` state.
- Channel allocation helpers derive HDMI Audio InfoFrame channel allocation and ALSA chmap controls from ELD speaker data.
- `had_prog_status_reg()`, `had_prog_dip()`, `had_prog_n()`, `had_prog_cts()`, and `had_init_audio_ctrl()` program channel status, infoframe, clocking, and core audio configuration.
- Ring helpers `had_init_ringbuf()`, `had_prog_bd()`, `had_process_ringbuf()`, and `had_pcm_pointer()` map the ALSA ring to four hardware buffer descriptors.
- ALSA callbacks `had_pcm_open()`, `close()`, `prepare()`, `trigger()`, `sync_stop()`, and `pointer()` provide playback operation.
- `display_pipe_interrupt_handler()` acknowledges per-pipe buffer-done/underrun IRQs and dispatches them to port contexts.
- `had_audio_wq()` processes i915 hotplug/ELD notifications under a workqueue and runtime PM.
- `__hdmi_lpe_audio_probe()` creates the ALSA card, PCMs, controls, jacks, IRQ, MMIO mapping, and i915 notification callback.

## Control Flow
Probe receives i915 platform data, maps MMIO, requests IRQ, sets a 32-bit DMA mask, initializes per-port `snd_intelhad` contexts, creates playback-only PCM devices, registers IEC958/ELD/chmap controls and jacks, registers the ALSA card, stores `notify_audio_lpe` into i915 platform data, enables runtime PM, and schedules initial work for all ports. On hotplug, i915 calls `notify_audio_lpe()`, which schedules `had_audio_wq()`. The workqueue copies ELD, updates DP/HDMI clock state, transitions connected state, rebuilds channel map, reports jack state, assigns pipe, and may reprogram N/CTS for an active stream.

For playback, ALSA open resumes runtime PM and exposes the active substream. Prepare programs N/CTS/DIP/status/audio-control registers and initializes the four-BD hardware ring. Trigger START/RESUME/PAUSE_RELEASE acknowledges stale IRQs and sets `aud_en`; STOP/PAUSE disables it. IRQs ack sticky status bits, advance/reprogram BDs on buffer-done, call `snd_pcm_period_elapsed()`, and stop with xrun on underrun or disconnect.

## State And Persistence
`snd_intelhad_card` persists card-wide MMIO, IRQ, port/pipe counts, and three per-port contexts. Each `snd_intelhad` tracks connection, ELD, DP/HDMI clocking, pipe/port, jack, channel map, cached `aud_config`, current substream plus refcount, spinlock, mutex, and ring indices (`bd_head`, `pcmbuf_head`, `pcmbuf_filled`). State is in kernel memory only and is reset on driver removal or hot-unplug. Runtime PM state persists through autosuspend.

## Dependencies And Integration Points
Depends on ALSA core/PCM/control/jack APIs, Linux platform device, MMIO, IRQ, DMA, runtime PM, DRM ELD helpers, and `drm/intel/intel_lpe_audio.h` platform data from i915. Hardware register definitions come from `intel_hdmi_lpe_audio.h`; private data structures come from `intel_hdmi_audio.h`.

## Risks
- Hardware has a documented AUD_CONFIG read/modify/write bug, so cached config must remain authoritative.
- The substream refcount wait in close busy-spins with `cpu_relax()` until IRQ/work users release the substream.
- `had_process_ringbuf()` treats invalid BD length or all-empty descriptors as xrun; hardware register anomalies can stop playback.
- Hotplug changes can stop active streams and reassign pipes; ordering between connected state and `ctx->pipe` changes is subtle.
- DP clocking supports only fixed link rates defined in the header; unsupported link rates cause `-EINVAL`.
- Channel map allocation mutates `eld[DRM_ELD_SPEAKER]` for a workaround, so ELD-derived data is not purely read-only.

## Test Signals
Test probe with valid i915 platform data, no platform data, MMIO/IRQ failure paths, HDMI and DP hotplug/unplug, ELD speaker masks, channel map control reads, IEC958 control changes, playback at every advertised rate/format/channel count, period sizes aligned to 64 bytes, underrun IRQs, runtime suspend/resume, and `single_port=1`. Inspect jack reports, xrun behavior, and buffer pointer monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.h -->
# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.h

## Purpose
Defines private structures and channel/speaker mapping types for the Intel HDMI/DP LPE audio driver.

## Important APIs, Types, And Functions
- Constants include `MAX_PB_STREAMS`, `MAX_CAP_STREAMS`, `BYTES_PER_WORD`, and driver name `INTEL_HAD`.
- `enum cea_speaker_placement` defines bit positions for CEA speaker layout.
- `struct cea_channel_speaker_allocation` and `struct channel_map_table` support InfoFrame channel allocation and ALSA channel-map control generation.
- `struct pcm_stream_info` stores the active ALSA substream and an IRQ/work refcount.
- `struct snd_intelhad` is the per-port runtime context.
- `struct snd_intelhad_card` is the card-wide context with ALSA card, MMIO, IRQ, pipe/port counts, and per-port contexts.

## Control Flow
The header has no direct flow; `intel_hdmi_audio.c` fills these structures during probe, hotplug, ALSA open/close/prepare/trigger, and IRQ handling.

## State And Persistence
The main state holders are `snd_intelhad` and `snd_intelhad_card`. They persist for the ALSA card lifetime and include connection status, ELD, DP flag, stream refcount, register cache, ring indices, work item, mutex, spinlock, and jack/channel-map objects.

## Dependencies And Integration Points
Includes `intel_hdmi_lpe_audio.h` for register constants and uses ALSA/DRM types through source inclusions. It binds private driver logic to i915-provided platform data and ALSA PCM/control objects.

## Risks
`pcm_ctx[3]` assumes a maximum of three ports/pipes. Refcount and lock fields in `snd_intelhad` must be used consistently because IRQ and workqueue paths dereference the active substream.

## Test Signals
Compile tests with different i915 platform-data port counts, plus runtime hotplug and close-while-IRQ tests that stress fields declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_lpe_audio.h -->
# sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_lpe_audio.h

## Purpose
Defines Intel HDMI/DP LPE audio hardware constants, register offsets, register bitfields, buffer limits, audio sample-rate constants, and HDMI/DP InfoFrame/clocking values.

## Important APIs, Types, And Functions
- PCM constraints include channel, buffer, period, FIFO, and rate limits.
- `enum hdmi_ctrl_reg_offset_common` and `enum hdmi_ctrl_reg_offset` define MMIO layout.
- Unions such as `aud_cfg`, `aud_ch_status_0`, `aud_ch_status_1`, `aud_hdmi_cts`, `aud_hdmi_n_enable`, `aud_buf_addr`, `aud_buf_len`, `aud_ctrl_st`, and `aud_info_frame*` define register-level bit layout.
- Constants define DP link rates, DP MAUD/NAUD values, HDMI N values, DIP words, IRQ status bits, and buffer descriptor flags.

## Control Flow
No executable flow. `intel_hdmi_audio.c` uses these definitions to program channel status, N/CTS or MAUD/NAUD, DIP packets, FIFO thresholds, buffer descriptors, and interrupt acknowledgments.

## State And Persistence
The header defines register value layout rather than storing state. `union aud_cfg` is cached in `snd_intelhad` to work around hardware read/modify/write behavior.

## Dependencies And Integration Points
Integrates directly with MMIO programming in the Intel LPE driver and with the hardware programming model for HDMI/DP audio on supported Atom platforms.

## Risks
Incorrect bitfield layout or constants directly misprogram hardware. Fixed DP link-rate tables mean unsupported link rates must be rejected or extended. Buffer constants enforce 20-bit aligned addresses and 64-byte period alignment assumptions.

## Test Signals
Playback at every advertised rate on HDMI and DP, IRQ status clearing, one-period buffer behavior, four-BD wraparound, and register tracing around prepare/trigger paths validate the constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/x86/intel_hdmi_lpe_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/Kconfig -->
# sources/distributed-fs/ceph-client/sound/xen/Kconfig

## Purpose
Defines the Xen para-virtualized sound frontend driver configuration.

## Important APIs, Types, And Functions
- `config SND_XEN_FRONTEND` is a tristate option for Xen guest sound frontend support.
- It depends on `XEN` and selects `SND_PCM`, `XEN_XENBUS_FRONTEND`, and `XEN_FRONT_PGDIR_SHBUF`.

## Control Flow
When enabled, the driver is built and can register a XenBus frontend for `XENSND_DRIVER_NAME`.

## State And Persistence
The Kconfig symbol persists in kernel build configuration and controls whether the module is available to Xen guests.

## Dependencies And Integration Points
Connects the Xen sound frontend source files in the Makefile to XenBus, shared grant-table page-directory buffers, and ALSA PCM.

## Risks
Missing selected dependencies would break the ALSA or Xen shared-buffer code. Runtime still requires a compatible Xen backend and matching page size.

## Test Signals
Build with `CONFIG_SND_XEN_FRONTEND=m/y`, boot in Xen guest, and verify the frontend appears only when Xen support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/Makefile -->
# sources/distributed-fs/ceph-client/sound/xen/Makefile

## Purpose
Builds the Xen sound frontend composite object.

## Important APIs, Types, And Functions
- `snd_xen_front-y` includes `xen_snd_front.o`, `xen_snd_front_cfg.o`, `xen_snd_front_evtchnl.o`, and `xen_snd_front_alsa.o`.
- `obj-$(CONFIG_SND_XEN_FRONTEND) += snd_xen_front.o` links the composite object conditionally.

## Control Flow
Kbuild compiles all frontend pieces as one module/built-in object when `CONFIG_SND_XEN_FRONTEND` is enabled.

## State And Persistence
No runtime state. Build inclusion is determined by kernel config.

## Dependencies And Integration Points
Pairs with `sound/xen/Kconfig` and the Xen/ALSA source modules in this directory.

## Risks
Adding a new frontend source without updating `snd_xen_front-y` would create unresolved symbols or omit functionality.

## Test Signals
`make M=sound/xen` with the config enabled should produce `snd_xen_front`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.c -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.c

## Purpose
Implements the Xen sound frontend core: XenBus driver registration/state handling and synchronous request helpers for backend stream operations.

## Important APIs, Types, And Functions
- `be_stream_prepare_req()`, `be_stream_do_io()`, and `be_stream_wait_io()` prepare a ring request, push it to the backend, and wait for completion.
- Public stream helpers issue `XENSND_OP_HW_PARAM_QUERY`, `OPEN`, `CLOSE`, `WRITE`, `READ`, and `TRIGGER`.
- `sndback_changed()` drives frontend behavior from backend XenBus state transitions.
- `sndback_initwait()` reads XenStore config, creates event channels, and publishes ring refs/ports.
- `sndback_connect()` creates ALSA card/PCM devices once backend reaches Connected.
- `xen_drv_probe()`, `xen_drv_remove()`, `xen_drv_init()`, and `xen_drv_fini()` implement XenBus module lifecycle.

## Control Flow
On module init, the driver checks it runs in a Xen PV-capable domain and that `XEN_PAGE_SIZE == PAGE_SIZE`, then registers as a XenBus frontend. Probe allocates `xen_snd_front_info` and switches to Initialising. On backend InitWait, the frontend disconnects stale state, parses XenStore, allocates/publishes request and event channels, then switches Initialised. On backend Connected, it initializes ALSA and switches Connected. Closing/Closed/Unknown states free ALSA and event-channel resources.

Synchronous stream operations serialize on `req_io_lock`, fill one request under `ring_io_lock`, flush the ring/event channel, and wait up to `VSND_WAIT_BACK_MS` for the matching response interrupt to complete.

## State And Persistence
`xen_snd_front_info` stores the XenBus device, ALSA card info, event-channel pairs, and parsed config. Request channels store ids and completions so one outstanding request per stream is serialized. No disk persistence; configuration is sourced from XenStore and rebuilt on reconnect.

## Dependencies And Integration Points
Depends on XenBus, Xen page/grant helpers, `xen-front-pgdir-shbuf`, `xen/interface/io/sndif.h`, `xen_snd_front_cfg`, `xen_snd_front_evtchnl`, and `xen_snd_front_alsa`.

## Risks
- Backend is assumed to respond within 3 seconds; timeout propagates to ALSA operations.
- Removal manually polls backend state because normal XenBus callbacks are disconnected.
- Only matching Xen/kernel page sizes are supported.
- Unexpected backend reset triggers disconnect/reinitialize paths that must free all old event channels and cards safely.

## Test Signals
Boot in Xen guest with a compatible backend, exercise backend state transitions InitWait/Connected/Closed, timeout a request, remove the frontend module, simulate backend restart, and verify ALSA devices disappear/reappear without leaked event channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.h -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.h

## Purpose
Declares the core Xen sound frontend context and synchronous stream operation APIs used by the ALSA layer.

## Important APIs, Types, And Functions
- `struct xen_snd_front_info` ties together XenBus device, ALSA card info, event-channel pairs, and parsed XenStore configuration.
- Declares query, prepare/open, close, write, read, and trigger helpers taking a request event channel.

## Control Flow
No executable flow. It defines the call path from ALSA callbacks into Xen backend operations: query constraints, open shared buffer, transfer bytes, trigger stream state, and close.

## State And Persistence
The declared frontend context is rebuilt from XenStore and backend state. It is stored as XenBus device driver data and persists for the device lifetime.

## Dependencies And Integration Points
Includes `xen_snd_front_cfg.h` and forward-declares event-channel, card, shared-buffer, and protocol request types. Used by all Xen sound frontend source files.

## Risks
All exported stream helpers assume a valid connected request channel. Callers must manage event-channel state and shared-buffer lifetime.

## Test Signals
Compile coverage plus runtime ALSA open/close/read/write/trigger operations validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.c -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.c

## Purpose
Implements the ALSA-facing layer of the Xen para-virtual sound frontend. It creates ALSA cards/PCM devices from XenStore config, refines hardware parameters with backend queries, manages shared grant-table audio buffers, and maps ALSA PCM callbacks to Xen sound protocol operations.

## Important APIs, Types, And Functions
- Runtime structures represent card, PCM instance, and per-stream state, including `xen_front_pgdir_shbuf`, buffer pages, stream index, hardware constraints, open state, and atomic hardware pointer.
- `ALSA_SNDIF_FORMATS`, `to_sndif_format()`, `to_sndif_formats_mask()`, and `to_alsa_formats_mask()` translate ALSA and Xen sample format encodings.
- `alsa_hw_rule()` sends `XENSND_OP_HW_PARAM_QUERY` to refine formats, rates, channels, buffer, and period sizes.
- `alsa_open()` installs configured hardware constraints, connects the stream event pair, attaches the substream to async event handling, and installs refinement rules.
- `alsa_hw_params()` allocates exact pages, creates a Xen frontend page-directory shared buffer, and maps it.
- `alsa_prepare()` sends `XENSND_OP_OPEN` with shared-buffer grant directory and PCM params.
- Playback/capture `.copy` callbacks move bytes to/from the shared buffer and issue `WRITE`/`READ` requests.
- `xen_snd_front_alsa_handle_cur_pos()` consumes backend current-position events, advances the atomic hw pointer, and emits ALSA period elapsed notifications.
- `new_pcm_instance()`, `xen_snd_front_alsa_init()`, and `xen_snd_front_alsa_fini()` create and destroy ALSA card/PCM state.

## Control Flow
After backend connection, `xen_snd_front_alsa_init()` creates one ALSA card and a PCM for each configured XenStore PCM instance. Opening a substream assigns its event-channel pair, clears stream state, marks channels connected, and adds dynamic hardware rules. During hw_params, the driver allocates a contiguous virtual buffer, collects pages, grants/maps the page directory, and stores shared-buffer metadata. Prepare opens the stream at the backend with the selected format/channel/rate and buffer/period sizes. Playback copies user data into the shared buffer then sends WRITE; capture sends READ then copies data out. Backend `CUR_POS` events update the ALSA pointer and signal periods.

## State And Persistence
Per-stream state owns shared-buffer pages, grant-directory state, open flag, event-pair pointer, current backend frame, atomic hw pointer, and period modulo. `stream_free()` unmaps/free grants and pages and resets fields. No disk persistence; all ALSA devices are regenerated from XenStore on backend connect.

## Dependencies And Integration Points
Depends on ALSA card/PCM/hw-rule APIs, XenBus, `xen-front-pgdir-shbuf`, `xen_snd_front` protocol helpers, parsed config from `xen_snd_front_cfg.c`, and event positions from `xen_snd_front_evtchnl.c`.

## Risks
- `alsa_hw_rule()` performs backend I/O during constraint refinement; backend latency/failure can affect ALSA parameter negotiation.
- Shared-buffer allocation uses `alloc_pages_exact()` and page arrays; failures must unwind all partially allocated grant resources.
- `alsa_hw_free()` always attempts backend close before freeing, so backend errors propagate during ALSA cleanup.
- `xen_snd_front_alsa_handle_cur_pos()` assumes the substream is valid when event channel is connected.
- Period notification uses `out_frames > period_size`; exact equality does not notify until more frames arrive.
- Mmap is intentionally unsupported because there is no user-space completion acknowledgement.

## Test Signals
Test playback and capture `.copy` paths, dynamic hw-params refinement, unsupported formats, backend query timeout, hw_params failure unwind, close after partial open, current-position event progression/wraparound, and backend reconnect. KASAN/lockdep are useful around shared-buffer free and async events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.h -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.h

## Purpose
Declares the ALSA integration entry points for the Xen sound frontend.

## Important APIs, Types, And Functions
- `xen_snd_front_alsa_init()` creates ALSA card/PCM devices from parsed XenStore configuration.
- `xen_snd_front_alsa_fini()` frees ALSA card state.
- `xen_snd_front_alsa_handle_cur_pos()` handles backend current-position events for period/pointer updates.

## Control Flow
The XenBus core calls init on backend Connected and fini during disconnect/remove. Event-channel interrupt handling calls `handle_cur_pos()` for `XENSND_EVT_CUR_POS`.

## State And Persistence
The header declares operations over `xen_snd_front_info` and event-channel state; actual ALSA/card/stream state lives in the C file and persists only for the connected backend session.

## Dependencies And Integration Points
Forward-declares `xen_snd_front_info` and uses `xen_snd_front_evtchnl` through the event callback declaration. Included by XenBus core and event-channel implementation.

## Risks
Callers must avoid calling `handle_cur_pos()` after stream teardown; event-channel connected state is the guard.

## Test Signals
Backend connect/disconnect and injected position events exercise all declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_alsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.c -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.c

## Purpose
Parses XenStore sound-card configuration into ALSA hardware constraints, PCM instances, and stream descriptors for the Xen sound frontend.

## Important APIs, Types, And Functions
- `CFG_HW_SUPPORTED_RATES` and `CFG_HW_SUPPORTED_FORMATS` map XenStore string tokens to ALSA rate/format masks.
- `SND_DRV_PCM_HW_DEFAULT` provides fallback PCM constraints.
- `cfg_read_pcm_hw()` inherits parent constraints and applies XenStore overrides for channels, sample rates, sample formats, and buffer size.
- `cfg_get_stream_type()` counts playback versus capture streams.
- `cfg_stream()` fills a stream descriptor, assigns the global stream index, stores its XenStore path, and reads stream-level constraints.
- `cfg_device()` parses one PCM device node and allocates playback/capture stream arrays.
- `xen_snd_front_cfg_card()` parses the whole card under the XenBus node and returns total stream count.

## Control Flow
Card parsing counts numeric device nodes under the frontend XenBus path. It reads default card hardware, allocates `pcm_instances`, then parses each device. Device parsing reads optional name and hardware overrides, counts numeric stream nodes up to `VSND_MAX_STREAM`, allocates playback/capture stream arrays, and fills each stream. Constraint inheritance flows card -> device -> stream.

## State And Persistence
Parsed state is stored in `front_info->cfg` using devm-managed arrays tied to the XenBus device. XenStore is the persistent source of truth; kernel state is rebuilt on backend init/reinit.

## Dependencies And Integration Points
Depends on XenBus reads/existence checks, Xen sound interface string constants, ALSA `snd_pcm_hardware`, and the ALSA creation code in `xen_snd_front_alsa.c`.

## Risks
- Unknown sample-rate or format strings are silently ignored; if all are unknown, inherited/default constraints remain.
- `rate_min` initializes to unsigned `-1`, relying on wrap to pick the first valid rate.
- `period_bytes_max` is forced to `buffer_bytes_max` and `periods_max` depends on `period_bytes_min`; invalid small/zero values would be dangerous, though defaults avoid zero.
- Numeric device/stream enumeration stops at the first missing node.

## Test Signals
Use XenStore configs with multiple devices, mixed playback/capture streams, per-card/device/stream overrides, missing stream type, invalid type, invalid format/rate strings, no devices, and maximum stream counts. Verify resulting ALSA PCM constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.h -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.h

## Purpose
Defines the parsed XenStore configuration structures for the Xen sound frontend.

## Important APIs, Types, And Functions
- `struct xen_front_cfg_stream` stores global stream index, XenStore path, and ALSA hardware constraints.
- `struct xen_front_cfg_pcm_instance` stores PCM name/device id, inherited hardware constraints, and playback/capture stream arrays.
- `struct xen_front_cfg_card` stores card names, default hardware constraints, and PCM instances.
- `xen_snd_front_cfg_card()` fills the card config and returns stream count.

## Control Flow
No executable flow. The structures describe the output of XenStore parsing and the input to event-channel creation and ALSA PCM creation.

## State And Persistence
Config structures persist for the frontend device lifetime and are regenerated from XenStore after reconnect. `xenstore_path` points to devm-allocated strings from parsing.

## Dependencies And Integration Points
Includes ALSA core/PCM headers for `snd_pcm_hardware`. Used by core, event-channel, and ALSA Xen frontend files.

## Risks
The global stream index must match event-channel pair indices; misordered parsing would connect ALSA streams to the wrong backend stream.

## Test Signals
Compile plus runtime multi-device/multi-stream configuration tests validate structure ownership and indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.c -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.c

## Purpose
Allocates, publishes, handles, and frees Xen event channels and shared rings for each Xen sound stream. It provides one request/response channel and one async event channel per stream.

## Important APIs, Types, And Functions
- `evtchnl_interrupt_req()` consumes backend responses from a Xen ring, matches the current request id, stores status/response payload, and completes waiters.
- `evtchnl_interrupt_evt()` consumes async events from the event page and dispatches current-position updates to ALSA.
- `xen_snd_front_evtchnl_flush()` pushes one request and notifies the backend.
- `evtchnl_alloc()` sets up a grant-backed page, event channel port, IRQ binding, and threaded IRQ handler.
- `xen_snd_front_evtchnl_create_all()` allocates request/event pairs for every configured stream.
- `xen_snd_front_evtchnl_publish_all()` writes ring refs and event-channel ports to XenStore in a transaction.
- `xen_snd_front_evtchnl_pair_set_connected()` and `xen_snd_front_evtchnl_pair_clear()` manage stream connection and event ids.

## Control Flow
During frontend InitWait, `create_all()` allocates all channel pairs following configured stream indices. `publish_all()` transactionally writes request ring ref/port and event ring ref/port under each stream's XenStore path. Stream operations fill request slots and call `flush()`. Request IRQs drain responses, use memory barriers around producer indexes, and complete the synchronous waiter. Async event IRQs drain event-page entries, enforce monotonically expected ids, and pass current-position events to ALSA.

## State And Persistence
Each channel stores grant ref, event port, IRQ, index, state, type, current/next event ids, ring lock, and union-specific request or event-page state. Channel state is transient; XenStore-published refs/ports advertise it to the backend until freed or backend resets.

## Dependencies And Integration Points
Depends on Xen event, grant-table, XenBus ring setup/teardown, Xen sound protocol definitions, parsed config, and ALSA current-position handling. It is called by `xen_snd_front.c` for lifecycle and by stream operations for request flushing.

## Risks
- The code trusts backend ring counters and event ids enough to avoid overflow validation.
- `evtchnl_alloc()` fail paths return after partial setup; caller frees all pairs, but individual partial resources must be initialized consistently.
- Request matching ignores responses with unexpected ids, so a lost/mismatched response can cause timeout.
- Async current-position events require `substream` to be valid while channel is connected.
- Transaction publish retries only on `-EAGAIN`; other failures call `xenbus_dev_fatal()`.

## Test Signals
Test allocation failure at ring, event-channel, IRQ bind, and request IRQ stages; XenStore transaction retry; backend response id mismatch; current-position event id gaps; disconnect while a request waits; and backend reset with all resources freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.h -->
# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.h

## Purpose
Declares Xen sound frontend event-channel states, channel structures, channel-pair structures, and lifecycle/utility APIs.

## Important APIs, Types, And Functions
- `VSND_WAIT_BACK_MS` defines backend response timeout.
- `enum xen_snd_front_evtchnl_state` and `enum xen_snd_front_evtchnl_type` classify connection state and request/event channel role.
- `struct xen_snd_front_evtchnl` stores grant ref, event port, IRQ, stream index, ids, ring lock, and request/event union state.
- `struct xen_snd_front_evtchnl_pair` groups request and event channels for one stream.
- Declares create/free/publish/flush/connect/clear helpers.

## Control Flow
No direct flow, but it defines the objects used by XenBus init, synchronous stream requests, IRQ callbacks, ALSA open/close connection toggles, and frontend cleanup.

## State And Persistence
Channel state persists while the backend session is active. Request channels include a completion and latest response status; event channels include an event page and attached ALSA substream pointer.

## Dependencies And Integration Points
Includes Xen sound protocol definitions and forward-declares `xen_snd_front_info`. Shared by all Xen sound frontend modules.

## Risks
The union makes channel type correctness important. Accessing request fields on an event channel or vice versa would corrupt state.

## Test Signals
Compile-time structure use plus runtime request timeout, async position event, open/close, and disconnect paths validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/Makefile -->
# sources/distributed-fs/ceph-client/tools/Makefile

## Purpose
Top-level Linux tools Makefile. It advertises available tool targets and dispatches build, install, and clean commands into subdirectories.

## Important APIs, Types, And Functions
- Exports empty `srctree` and `objtree` for tools using kernel-like variables.
- Includes `scripts/Makefile.include` for `descend` and common Kbuild helpers.
- Defines individual targets such as `perf`, `selftests`, `cpupower`, `objtool`, `ynl`, and many others.
- Defines aggregate `all`, `install`, and `clean` targets.

## Control Flow
Most targets call `$(call descend,<dir>[,<target>])`. `perf` is special and invokes `make -C perf O=$(PERF_O) subdir=`. Install and clean targets mirror build targets with `_install` and `_clean` suffixes.

## State And Persistence
No runtime state. Build artifacts are produced in tool subdirectories and optionally under `O=` output trees; `PERF_O` maps `O` to `$(O)/tools/perf`.

## Dependencies And Integration Points
Integrates all kernel userspace tools and relies on each subdirectory Makefile. The accounting tools in this subset are not directly listed here, so they are built by entering `tools/accounting` explicitly or through external packaging.

## Risks
Aggregate targets can be broad and expensive. Target names must stay synchronized with available subdirectories. `clean` dispatch can remove many generated outputs.

## Test Signals
Run `make -C tools help`, selected targets, install targets with `DESTDIR`, and clean targets. Verify `O=` handling for `perf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/Makefile -->
# sources/distributed-fs/ceph-client/tools/accounting/Makefile

## Purpose
Builds task/accounting demonstration utilities.

## Important APIs, Types, And Functions
- `CC := $(CROSS_COMPILE)gcc` supports cross-compilation.
- `CFLAGS := -I../include/uapi/` points builds at local UAPI headers.
- `PROGS := getdelays procacct delaytop` lists the built programs.
- `all` builds all programs; `clean` removes them.

## Control Flow
Default implicit C build rules compile each program from its matching `.c` file. `clean` removes binaries.

## State And Persistence
No runtime state. Build outputs are the three binaries in the accounting directory.

## Dependencies And Integration Points
Depends on local UAPI headers and libc/system netlink headers. The programs interact with Linux taskstats/cgroupstats/PSI at runtime.

## Risks
Implicit rules mean per-program extra libraries or flags must be added explicitly if future code needs them. `clean` uses `rm -fr $(PROGS)`.

## Test Signals
Run `make -C tools/accounting` and `make clean`; execute each binary with `--help` or basic arguments on a kernel with taskstats enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/delaytop.c -->
# sources/distributed-fs/ceph-client/tools/accounting/delaytop.c

## Purpose
Provides a top-like userspace monitor for system pressure, cgroup statistics, and per-task delay accounting. It samples PSI from `/proc/pressure`, fetches taskstats over generic netlink, sorts tasks by selected delay metric, and supports interactive key handling.

## Important APIs, Types, And Functions
- `struct psi_stats`, `task_info`, `container_stats`, `field_desc`, and `config` hold sampled data and UI/settings state.
- Netlink helpers `create_nl_socket()`, `send_cmd()`, and `get_family_id()` access the `TASKSTATS` generic netlink family.
- `read_psi_stats()` parses CPU/memory/IO/IRQ PSI files.
- `fetch_and_fill_task_info()` requests `TASKSTATS_CMD_ATTR_PID` and copies delay fields into `tasks[]`.
- `get_task_delays()` scans `/proc` or one PID and fills up to `MAX_TASKS`.
- `get_container_stats()` sends `CGROUPSTATS_CMD_GET` for a cgroup path.
- `compare_tasks()` sorts by average delay using configured field offsets.
- `display_results()`, `check_for_keypress()`, and `handle_keypress()` implement terminal output and interactive mode switching/sorting.

## Control Flow
`main()` parses options, opens a generic netlink socket, discovers the taskstats family id, puts the terminal in raw mode, and loops until iteration count, one-shot mode, or quit. Each iteration verifies display mode/sort compatibility, reads PSI, optionally reads cgroup stats, fetches task delay stats, sorts the global task array, renders the screen, waits for keyboard input with `select()`, and handles mode/sort/quit commands.

## State And Persistence
State is process-local globals: current config, PSI sample, task array, task count, running flag, container stats, netlink socket, family id, and terminal mode. There is no file persistence. It temporarily changes terminal settings and restores them on normal exit.

## Dependencies And Integration Points
Depends on Linux generic netlink, `linux/taskstats.h`, `linux/cgroupstats.h`, `/proc`, `/proc/pressure/*`, and terminal APIs. It integrates with kernel delay accounting and PSI facilities; meaningful data requires kernel support and permissions to query taskstats.

## Risks
- `enable_raw_mode()` lacks signal/atexit restoration, so abnormal termination can leave terminal settings changed.
- `compare_tasks()` reads count fields as `unsigned long` even fields are `unsigned long long`, which can truncate on 32-bit builds.
- Per-PID netlink queries while scanning `/proc` can race with process exit and print many transient errors.
- `get_container_stats()` passes `&cfd` with `sizeof(__u32)`; this relies on fd size matching u32 representation.
- `read_psi_stats()` returns warning counts as truthy; UI prints "PSI not found" for any warning, not just missing PSI.

## Test Signals
Run `delaytop -o`, `-p <pid>`, `-M`, `-s` for every field, `-C <cgroup>`, and interactive `o/M/q`. Test with PSI disabled, taskstats unavailable, rapidly exiting tasks, non-TTY stdin, and 32-bit builds if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/delaytop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/getdelays.c -->
# sources/distributed-fs/ceph-client/tools/accounting/getdelays.c

## Purpose
Demonstrates and exposes Linux taskstats delay accounting, IO accounting, context-switch counts, and cgroupstats through generic netlink. It can query a pid/tgid, register a CPU mask for exit notifications, run a command and report its stats, or query cgroup stats.

## Important APIs, Types, And Functions
- Generic netlink helpers `create_nl_socket()`, `recv_taskstats_msg()`, `send_cmd()`, and `get_family_id()`.
- `format_timespec()` formats version 17 taskstats max-delay timestamps.
- Print macros handle taskstats version compatibility for delay max/min and timestamp fields.
- `print_delayacct()`, `task_context_switch_counts()`, `print_cgroupstats()`, and `print_ioacct()` render decoded stats.
- `main()` parses options, registers/deregisters cpumasks, sends pid/tgid/cgroup commands, optionally waits for a forked command, and parses netlink replies.

## Control Flow
The program discovers the taskstats family, optionally registers a CPU mask, validates mutually exclusive pid/cgroup selections, waits for a forked command when `-c` is used, sends one or more taskstats/cgroupstats requests, then receives messages in a loop. It parses top-level netlink attributes, descends into pid/tgid aggregate attributes, and prints selected stats or writes raw `taskstats` records to a file. Unless `-l` is set, it exits after one stats record.

## State And Persistence
State is process-local globals for receive buffer size, debug flag, print selections, taskstats family name, and cpumask. Optional raw stats persistence occurs through `-w logfile`, which writes binary taskstats payloads. Cpumask registration persists in the kernel only until deregistration or process/socket teardown.

## Dependencies And Integration Points
Depends on `NETLINK_GENERIC`, taskstats/cgroupstats UAPI, local taskstats versions, and standard POSIX process/signal APIs. It is a reference user for kernel delay accounting.

## Risks
- Netlink parsing trusts attribute lengths enough to step through nested attributes; malformed kernel responses are not heavily guarded.
- `-c` uses `sigwait()` instead of `waitpid()` to preserve exit data; child exit status is not surfaced.
- Binary logfile format is raw `struct taskstats`, so readers must match UAPI layout/version.
- cpumask registration should be deregistered on normal exit, but abrupt termination can rely on socket cleanup.

## Test Signals
Use `getdelays -d -p <pid>`, `-d -t <tgid>`, `-i -p`, `-q`, `-C <cgroup>`, `-m <cpumask> -l`, `-c <command>`, and `-w` output. Validate taskstats version-dependent fields on kernels with versions below and above 16/17.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/getdelays.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/procacct.c -->
# sources/distributed-fs/ceph-client/tools/accounting/procacct.c

## Purpose
Listens for taskstats process accounting records on task exit and prints compact process/thread resource usage, including executable device/inode metadata when available.

## Important APIs, Types, And Functions
- Reuses generic netlink helpers for socket creation, message receive, command send, and family discovery.
- `print_procacct()` formats taskstats accounting fields: pid, tgid, uid, elapsed time, group walltime, CPU time, peak VM/RSS, executable dev/inode, and command.
- `handle_aggr()` parses nested pid/tgid aggregate attributes and prints only pid aggregate stats.
- `main()` parses cpumask/debug/log options, defaults cpumask to `1`, registers the mask, and receives taskstats indefinitely.

## Control Flow
Startup selects a cpumask, optionally opens a raw output file, creates a generic netlink socket, discovers taskstats family id, and registers the cpumask for exit notifications. The receive loop decodes each netlink message, calls `handle_aggr()` for pid/tgid aggregates, writes raw taskstats data if requested, and continues forever. On `done`, it deregisters the cpumask.

## State And Persistence
State is global and process-local: socket buffer size, debug flag, family name, cpumask, and optional output file descriptor. `-w` persists raw taskstats payloads to a binary log. The cpumask registration is kernel state while the listener is active.

## Dependencies And Integration Points
Depends on generic netlink, `linux/taskstats.h`, `linux/acct.h`, `linux/kdev_t.h`, and kernel taskstats exit accounting. It complements `getdelays` by focusing on exit-time accounting rather than point queries.

## Risks
- Infinite receive loop requires external termination; normal deregistration may not run on signals.
- `send_cmd()` sets `nla_len = nla_len + 1 + NLA_HDRLEN`, unlike `getdelays`, which may be intentional for string cpumasks but should be scrutinized for non-string attributes.
- Only pid aggregate stats are printed by default; tgid aggregate handling is parsed but not printed.
- Raw log files depend on taskstats struct version and machine ABI.

## Test Signals
Run with default cpumask and create/exit processes, with `-m` for specific CPUs, `-v` debug output, `-r` buffer sizing, and `-w` raw output. Validate printed AGROUP/thread flags on kernels with taskstats version >= 12.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/accounting/procacct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/alpha/include/asm/barrier.h

## Purpose
Provides Alpha userspace tooling definitions for memory barrier primitives.

## Important APIs, Types, And Functions
- `mb()` and `rmb()` emit Alpha `mb`.
- `wmb()` emits Alpha `wmb`.

## Control Flow
No control flow; macros expand to inline assembly with a memory clobber.

## State And Persistence
No state. The macros constrain compiler and CPU memory ordering in tools code.

## Dependencies And Integration Points
Used by Linux tools, especially perf-style code, when building for Alpha.

## Risks
Incorrect barrier semantics would create subtle ordering bugs in lockless userspace tooling.

## Test Signals
Cross-compile tools for Alpha and inspect assembly or run concurrency tests using these barrier macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/bitsperlong.h

## Purpose
Defines Alpha UAPI long width for tools builds.

## Important APIs, Types, And Functions
- Sets `__BITS_PER_LONG` to `64`.
- Includes `asm-generic/bitsperlong.h` for generic definitions.

## Control Flow
No runtime flow.

## State And Persistence
No state. It affects compile-time ABI constants.

## Dependencies And Integration Points
Used by tools UAPI headers to size masks and syscall-facing types for Alpha.

## Risks
Changing this breaks Alpha ABI assumptions in tools.

## Test Signals
Cross-compile tools for Alpha and verify `sizeof(long)` assumptions and generated masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/errno.h

## Purpose
Provides Alpha-specific errno number definitions for tools UAPI builds.

## Important APIs, Types, And Functions
- Includes generic errno base definitions.
- Undefines generic `EAGAIN` and assigns Alpha-specific errno values.
- Defines networking, IPC, filesystem, stream, library, restart, medium, key, robust mutex, rfkill, and hardware poison errors.
- Aliases include `EWOULDBLOCK`, `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow
No runtime flow; this is compile-time constant mapping.

## State And Persistence
No state. Constants must match kernel/userspace ABI.

## Dependencies And Integration Points
Used by Linux tools built against copied UAPI headers for Alpha.

## Risks
Errno number mismatches would make tools misinterpret syscall or perf-event errors on Alpha.

## Test Signals
Cross-compile and run syscall/error-path tests on Alpha or compare constants against kernel UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/mman.h

## Purpose
Defines Alpha memory mapping, protection, and madvise constants for tools, including fallback constants missing on Alpha.

## Important APIs, Types, And Functions
- Defines `MADV_*`, `MAP_*`, and `PROT_*` constants with Alpha ABI values.
- Provides tool compatibility fallbacks for `MADV_HWPOISON`, `MADV_SOFT_OFFLINE`, `MAP_32BIT`, and `MAP_UNINITIALIZED`.

## Control Flow
No runtime flow.

## State And Persistence
No state. Constants affect compiled tools ABI.

## Dependencies And Integration Points
Used by tools such as perf that need mman constants across architectures.

## Risks
Wrong values can break mmap/madvise decoding or invocation in tools. Fallback constants set unsupported features to harmless or conventional values for build compatibility.

## Test Signals
Cross-compile perf/tools for Alpha and compare generated constants against Alpha UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/mman.h

## Purpose
Provides ARC tools mman compatibility by including generic mman constants and defining missing `MAP_32BIT`.

## Important APIs, Types, And Functions
- Includes `<uapi/asm-generic/mman.h>`.
- Defines `MAP_32BIT` as `0` for ARC.

## Control Flow
No runtime flow.

## State And Persistence
No state. Compile-time constants only.

## Dependencies And Integration Points
Used by tools builds that expect `MAP_32BIT` to exist across architectures.

## Risks
Code that tests `MAP_32BIT` must tolerate zero meaning unsupported/no-op on ARC.

## Test Signals
Cross-compile tools for ARC and ensure mman users build without architecture-specific ifdefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/unistd.h

## Purpose
Defines ARC syscall UAPI wiring for tools, including generic syscall inclusion and ARC-specific syscall numbers.

## Important APIs, Types, And Functions
- Guard permits inclusion twice when `__SYSCALL` is defined.
- Defines `__ARCH_WANT_*` feature macros for selected legacy/generic syscall wrappers.
- Aliases `sys_mmap2` to `sys_mmap_pgoff`.
- Includes `asm-generic/unistd.h`, defines `NR_syscalls`, `__NR_sysfs`, and ARC-specific syscalls: `cacheflush`, `arc_settls`, `arc_gettls`, and `arc_usr_cmpxchg`.
- Emits `__SYSCALL()` entries for ARC-specific and `sysfs` calls.

## Control Flow
No runtime flow; preprocessor controls syscall table generation and tools ABI constants.

## State And Persistence
No state. Constants and macros persist in compiled tools.

## Dependencies And Integration Points
Integrates with generic unistd headers and tools syscall decoding/generation for ARC.

## Risks
Incorrect syscall numbering or feature macros would break syscall tracing/decoding and tools that issue ARC-specific syscalls.

## Test Signals
Cross-compile syscall-aware tools for ARC and compare syscall numbers with kernel UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm/include/asm/barrier.h

## Purpose
Provides ARM userspace tooling memory barrier macros through the kernel user helper page.

## Important APIs, Types, And Functions
- `mb()`, `wmb()`, and `rmb()` call the function pointer at `0xffff0fa0`, the `__kuser_memory_barrier` helper.

## Control Flow
Macros perform a userspace helper call when expanded.

## State And Persistence
No stored state; they enforce memory ordering for tools code.

## Dependencies And Integration Points
Relies on the ARM kernel helper page ABI described by `arch/arm/kernel/entry-armv.S`.

## Risks
Requires environments where the kuser helper page is available/enabled. Barrier calls are function-pointer calls to a fixed address, so emulator or hardened configurations can matter.

## Test Signals
Build ARM tools and run barrier-dependent tests on ARM kernels with kuser helpers enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/mman.h

## Purpose
Provides ARM tools mman compatibility by including generic mman constants and defining missing `MAP_32BIT`.

## Important APIs, Types, And Functions
- Includes `<uapi/asm-generic/mman.h>`.
- Defines `MAP_32BIT` as `0` for ARM.

## Control Flow
No runtime flow.

## State And Persistence
No state; compile-time constants only.

## Dependencies And Integration Points
Used by tool code that references `MAP_32BIT` across architectures.

## Risks
`MAP_32BIT` is a no-op/unsupported marker on ARM, so callers must not expect x86 behavior.

## Test Signals
Cross-compile tools for ARM and verify mman users build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/perf_regs.h

## Purpose
Defines ARM register identifiers used by perf event sample register masks.

## Important APIs, Types, And Functions
- `enum perf_event_arm_regs` lists `R0` through `R10`, `FP`, `IP`, `SP`, `LR`, `PC`, and `PERF_REG_ARM_MAX`.

## Control Flow
No runtime flow.

## State And Persistence
No state. Enum values become ABI-facing register ids in tools.

## Dependencies And Integration Points
Used by perf and other tooling that decodes or requests ARM user register samples.

## Risks
Changing enum order breaks perf sample ABI interpretation.

## Test Signals
Run perf register sampling/decoding tests for ARM and compare ids against kernel UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/barrier.h

## Purpose
Provides AArch64 userspace tooling memory barrier and acquire/release primitives.

## Important APIs, Types, And Functions
- `mb()`, `wmb()`, and `rmb()` emit `dmb ish`, `dmb ishst`, and `dmb ishld`.
- `smp_mb()`, `smp_wmb()`, and `smp_rmb()` mirror those DMB variants.
- `smp_store_release(p, v)` emits size-specific `stlrb`, `stlrh`, or `stlr` for 1/2/4/8-byte stores.
- `smp_load_acquire(p)` emits size-specific `ldarb`, `ldarh`, or `ldar` for 1/2/4/8-byte loads.

## Control Flow
No ordinary flow; macros expand inline. Size switches select assembly forms and fall back to `mb()` for unexpected sizes to satisfy the compiler.

## State And Persistence
No state. The macros define ordering semantics for lockless tools code.

## Dependencies And Integration Points
Used by perf and other Linux tools on arm64. It relies on alias integer types such as `__u8_alias_t` being available from surrounding tool headers.

## Risks
Compiler/type assumptions are important because the macros use type-punning unions and alias types. Incorrect barriers can corrupt lockless ring-buffer or perf-event data handling.

## Test Signals
Cross-compile arm64 tools, run perf ring-buffer tests, and inspect generated assembly for load-acquire/store-release cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/brk-imm.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/brk-imm.h

## Purpose
Defines arm64 BRK immediate values used to identify software breakpoint/trap purposes.

## Important APIs, Types, And Functions
- Defines immediates for kprobes, uprobes, kprobe single-step, kretprobes, intentional fault, KGDB dynamic/compiled breakpoints, BUG/WARN traps, KASAN, UBSAN, and CFI traps.
- `CFI_BRK_IMM_TARGET`, `CFI_BRK_IMM_TYPE`, `CFI_BRK_IMM_BASE`, and `CFI_BRK_IMM_MASK` define CFI immediate bit fields.

## Control Flow
No runtime flow; constants are used by code that emits or decodes `BRK #imm16` instructions.

## State And Persistence
No state. Constants are ABI/debugging conventions between kernel and tools.

## Dependencies And Integration Points
Used by arm64 tooling and possibly disassembly/diagnostic paths that need to classify break instructions.

## Risks
Incorrect immediates can misclassify traps or conflict with reserved ranges, degrading debugging, sanitizers, probes, or CFI diagnostics.

## Test Signals
Compare against kernel arm64 `brk-imm.h`, run probe/BUG/KASAN/UBSAN/CFI decoding tests, and verify tools classify `BRK` immediates correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/brk-imm.h -->
