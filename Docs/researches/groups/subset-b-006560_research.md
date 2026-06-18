# subset-b-006560 Research

Grouped source-tree-aligned research for USB audio, hiFace, and Line 6 driver files under `sources/distributed-fs/ceph-client/sound/usb`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/card.h -->
# sources/distributed-fs/ceph-client/sound/usb/card.h

## Purpose
Defines the central in-memory model for the generic ALSA USB-audio driver: parsed audio formats, streaming endpoints, PCM substreams, stream containers, and optional platform callbacks. It is the shared contract consumed by format parsing, clock setup, endpoint streaming, PCM callbacks, quirks, and platform integration.

## Important APIs, Types, and State
`struct audioformat` records one USB alternate setting: ALSA format bitmask, channel count, UAC type/protocol, endpoint/sync endpoint coordinates, packet interval, max packet size, supported rates, clock ID, channel map, and DSD flags. `struct snd_usb_endpoint` models an isochronous data or sync endpoint with open/running state, endpoint callbacks, sync links, URB contexts, packet scheduling FIFO, clock/packet accumulators, hardware-constraint cache, and a spinlock. `struct snd_usb_substream` stores playback/capture state including current format, ALSA substream, endpoint handles, buffer accounting, DoP state, and stream flags. `struct snd_usb_stream` groups playback and capture substreams for one ALSA PCM. `struct snd_usb_platform_ops` provides connect/disconnect/suspend/resume hooks for external platform integration. Constants such as `MAX_URBS`, `MAX_PACKS_HS`, `SYNC_URBS`, and `MAX_QUEUE` bound URB fanout and queue depth.

## Control Flow and Integration
This header is included by `format.c`, `clock.c`, `endpoint.c`, `implicit.c`, and PCM code. Parser code fills `audioformat`; PCM hw_params opens an endpoint and passes selected format/rate/channel parameters; endpoint logic uses cached `audioformat` fields to allocate URBs and set interfaces/rates. `snd_usb_find_suppported_substream`, platform-op registration, and rediscovery declarations link this internal model to broader card/platform code outside this subset.

## State and Persistence
State is kernel-resident only. `audioformat` instances live on format lists, endpoints live on `chip->ep_list`, and substreams/streams live on `chip->pcm_list`. No persistent storage is used; suspend/resume and disconnect depend on callers resetting flags and freeing lists.

## Dependencies
Depends on Linux USB descriptors, ALSA PCM types, list heads, spinlocks/atomics, and local `struct snd_usb_audio` from `usbaudio.h`. Endpoint fields are tightly coupled to `endpoint.c` and PCM prepare/retire callbacks.

## Risks and Test Signals
Important risks are stale endpoint/substream pointers during disconnect, mismatched format/rate compatibility for shared endpoints, packet-size limits that must match USB speed, and DSD/DoP frame-size differences. Useful tests are USB-audio playback/capture across UAC1/UAC2/UAC3 devices, implicit feedback full duplex, DSD formats, suspend/resume, and module unload while streams are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/clock.c -->
# sources/distributed-fs/ceph-client/sound/usb/clock.c

## Purpose
Implements USB Audio Class clock topology walking and sample-rate setup for UAC1, UAC2, and UAC3 devices. It finds usable clock sources through source/selector/multiplier descriptors, validates clock availability, optionally auto-selects a valid selector input, and programs sample frequency controls.

## Important APIs and Functions
`snd_usb_clock_find_source()` is the exported topology resolver. It walks from `fmt->clock` to a terminal clock source with recursion detection through a 256-bit visited set. `snd_usb_init_sample_rate()` dispatches rate programming by protocol. `snd_usb_set_sample_rate_v2v3()` writes a UAC2/UAC3 clock source sample-frequency control and returns the observed rate. Helpers include descriptor validators, `uac_clock_selector_get_val()`, `uac_clock_selector_set_val()`, `uac_clock_source_is_valid()`, `set_sample_rate_v1()`, and `get_sample_rate_v2v3()`.

## Control Flow
For UAC2/UAC3, `snd_usb_clock_find_source()` calls `__uac_clock_find_source()`. If the entity is a clock source, optional validation reads the clock-valid control unless the descriptor says it is unreadable. If the entity is a selector, the current one-based pin is read, recursively resolved, and, when writable, written back or replaced by another valid source if `chip->autoclock` is enabled. Multipliers are treated as pass-through. For rate setup, UAC1 writes a three-byte endpoint sample-rate control and optionally reads it back. UAC2/UAC3 resolves a valid clock, reads the current rate, writes the desired rate if writable, applies TEAC interface-reset quirks when the base-rate family changes, and validates clock state again.

## State and Persistence
No persistent storage exists. Runtime state touched here includes `chip->sample_rate_read_error`, `chip->autoclock`, `chip->quirk_flags`, and device clock selector/current-rate state. Clock selector writes persist on the USB device until changed or reset.

## Dependencies and Integration
Uses local descriptor helpers, `snd_usb_ctl_msg()`, `snd_usb_find_ctrl_interface()`, UAC descriptor definitions, and quirk flags from `quirks.h`. Endpoint preparation calls `snd_usb_init_sample_rate()` through `endpoint.c`; format parsing calls `snd_usb_set_sample_rate_v2v3()` when validating supported rates.

## Risks and Test Signals
Descriptor length checks guard malformed devices, but selector control readability/writability and recursive descriptor graphs remain fragile. Device quirks for Denon DJ, MOTU AVB, TEAC, and ignored clock sources are critical behavior. Test with UAC2/UAC3 devices using selectors, read-only clocks, slow external clocks, invalid current selector values, and sample-rate changes across 44.1/48 kHz families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/clock.h -->
# sources/distributed-fs/ceph-client/sound/usb/clock.h

## Purpose
Declares the clock and sample-rate entry points used by USB-audio format and endpoint code.

## APIs and Integration
`snd_usb_init_sample_rate()` programs a selected `audioformat` to a runtime rate. `snd_usb_clock_find_source()` resolves the ultimate UAC2/UAC3 clock source, optionally validating it. `snd_usb_set_sample_rate_v2v3()` writes a UAC2/UAC3 clock source frequency control and returns the observed rate or an error. `endpoint.c` uses the first two for prepare-time setup; `format.c` uses the setter for rate-table validation.

## State, Dependencies, and Risks
The header depends on `struct snd_usb_audio`, `struct audioformat`, and `bool` being available from including translation units. Its risk is API misuse: callers must pass an initialized format with correct protocol/interface/clock fields and must hold appropriate higher-level endpoint or format context when changing device state.

## Test Signals
Compile coverage from all including files, plus runtime tests that exercise UAC1 and UAC2/UAC3 sample-rate setup, are sufficient to detect declaration/contract drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/endpoint.c -->
# sources/distributed-fs/ceph-client/sound/usb/endpoint.c

## Purpose
Provides the generic USB-audio endpoint streaming engine. It abstracts isochronous data and feedback endpoints, manages interface and clock refcounts, allocates URBs, calculates packet sizes, starts/stops streams, handles completion callbacks, and connects endpoint traffic to ALSA PCM data callbacks.

## Important APIs and Types
Public APIs include `snd_usb_add_endpoint()`, `snd_usb_get_endpoint()`, `snd_usb_endpoint_open()`, `snd_usb_endpoint_close()`, `snd_usb_endpoint_set_params()`, `snd_usb_endpoint_prepare()`, `snd_usb_endpoint_start()`, `snd_usb_endpoint_stop()`, `snd_usb_endpoint_release()`, `snd_usb_endpoint_free_all()`, `snd_usb_endpoint_set_sync()`, `snd_usb_endpoint_set_callback()`, `snd_usb_endpoint_get_clock_rate()`, `snd_usb_endpoint_next_packet_size()`, and `snd_usb_queue_pending_output_urbs()`. Private `snd_usb_iface_ref` and `snd_usb_clock_ref` objects serialize shared USB interface altsetting and shared clock rate use.

## Control Flow
Endpoint creation adds a data or sync endpoint to `chip->ep_list` and computes the pipe from endpoint direction. `snd_usb_endpoint_open()` is called from hw_params, records interface/altsetting/rate/format/period constraints on first open, verifies compatibility on later opens, and increments interface and clock open counts. `snd_usb_endpoint_set_params()` releases old URBs, computes nominal frequency, packets per second, small/large packet sizes, max frame sizes, and delegates to data or sync URB allocation. `snd_usb_endpoint_prepare()` deselects/selects interfaces, applies mode/pitch/rate setup, handles UAC1-vs-UAC2 order quirks, and clears setup flags. `snd_usb_endpoint_start()` increments running refs, locks clock rate, initializes accumulators, submits URBs or queues ready playback URBs for implicit feedback. Completion callbacks retire data, process sync feedback, prepare the next URB, and resubmit until stopped. Stop moves state from running to stopping, unlinks active URBs unless pending URBs are intentionally kept, and `wait_clear_urbs()` finalizes cleanup.

## State and Persistence
State is volatile and spread across atomics (`running`, `state`, `submitted_urbs`), bitmasks (`active_mask`, `unlink_mask`), packet FIFOs for implicit feedback, USB interface `altset`, clock `rate/locked/need_setup`, and endpoint flags `need_setup`/`need_prepare`. Device-visible state includes interface altsettings and sample rates programmed through `clock.c`; no disk persistence exists.

## Dependencies and Integration
Depends on ALSA PCM params, Linux USB URB APIs, `clock.c`, `helper.c`, PCM callbacks from `pcm.h`, and quirk hooks such as `snd_usb_select_mode_quirk()`, `snd_usb_init_pitch()`, and `snd_usb_endpoint_start_quirk()`. It is the runtime bridge between parsed `audioformat` objects and PCM data movement.

## Risks and Test Signals
Risks include races across completion callbacks and stop, refcount imbalance between open/start/stop/close, clock-rate conflicts on shared clocks, URB leaks after partial allocation, implicit-feedback FIFO overflow, bad packet-size math for high-speed intervals, and quirks that require nonstandard interface ordering. Test signals include playback/capture start-stop loops, low-latency playback, implicit feedback devices, sync endpoint feedback format detection, suspend/resume, disconnect while active, and KASAN/lockdep coverage for URB cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/endpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/endpoint.h -->
# sources/distributed-fs/ceph-client/sound/usb/endpoint.h

## Purpose
Declares the generic USB-audio endpoint lifecycle and streaming API used by PCM, implicit feedback, and setup code.

## APIs and Integration
The header defines endpoint types `SND_USB_ENDPOINT_TYPE_DATA` and `SND_USB_ENDPOINT_TYPE_SYNC`. It exposes functions to add/find endpoints, open/close them for a selected `audioformat`, set parameters, prepare interface/rate state, link sync endpoints, install data callbacks, start/stop/suspend/release/free endpoints, query shared clock rates, test compatibility, compute packet sizes, and queue pending output URBs. PCM code owns prepare/retire callbacks; endpoint code owns bus submission and feedback.

## State, Dependencies, and Risks
The functions operate on `struct snd_usb_audio`, `struct audioformat`, `struct snd_usb_endpoint`, `struct snd_usb_substream`, and ALSA hw params. Callers must respect lifecycle order: add, open, set params, prepare, set callbacks, start, stop, sync stop, close/release. Misordered calls can leave NULL interface refs, unmatched running refs, or active URBs during teardown.

## Test Signals
Compile-time inclusion by generic PCM code and runtime coverage of hw_params/prepare/trigger/hw_free paths are the main signals. Implicit feedback and shared-clock devices test the more subtle compatibility and sync APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/endpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/fcp.c -->
# sources/distributed-fs/ceph-client/sound/usb/fcp.c

## Purpose
Implements a Focusrite Control Protocol kernel shim for supported Focusrite USB audio interfaces. It exposes a privileged hwdep device for user-space protocol drivers, maintains a vendor notification URB, executes FCP USB command/response transactions, and provides one kernel ALSA control for frequent level-meter polling.

## Important APIs, Types, and Functions
`snd_fcp_init()` is the public initializer called from mixer setup. `struct fcp_data` stores mixer backpointer, protocol mutex, command completion, active hwdep file pointer, notify waitqueue/spinlock, vendor interface/endpoint coordinates, init opcodes/response sizes, sequence number, and meter-control buffers. `fcp_usb()` sends request packets with opcode/size/seq, waits for ACK from the notification URB, reads the response, and validates sequence/opcode/error/size. hwdep operations implement `FCP_IOCTL_PVERSION`, `FCP_IOCTL_INIT`, `FCP_IOCTL_CMD`, `FCP_IOCTL_SET_METER_MAP`, `FCP_IOCTL_SET_METER_LABELS`, read, poll, open, and release. Meter control callbacks provide integer level values and optional FCP TLV labels.

## Control Flow
Initialization allocates private state, finds the vendor-specific Focusrite control interface, and creates an exclusive hwdep device. User space opens hwdep with `CAP_SYS_RAWIO`, sends init parameters, and `fcp_init()` performs step0, starts the interrupt notification URB, resets sequence, sends two init opcodes, and returns init responses. Later `FCP_IOCTL_CMD` copies bounded user data, rejects dangerous flash erase/write requests against App_Gold segment 0, executes `fcp_usb()`, and copies the response back. Notification URB completion completes command ACKs and queues non-ACK event bits for `read()`/`poll()`, then resubmits while the device is alive. Meter reads reinitialize after suspend if needed, send `FCP_USB_GET_METER`, and remap device slots to ALSA channels.

## State and Persistence
All state is in `fcp_data` and `mixer->urb`. Sequence numbers increment per request. Meter map/labels persist only while the mixer instance exists. Suspend frees the notification URB; `fcp_reinit()` restores protocol state lazily. Device firmware state can be changed by user commands, except guarded App_Gold flash operations.

## Dependencies and Integration
Depends on ALSA hwdep/control/TLV APIs, USB mixer internals, `snd_usb_ctl_msg()`, UAPI `sound/fcp.h`, and Focusrite vendor descriptors. The private free/suspend hooks attach to `usb_mixer_interface`, while controls are registered through USB mixer helpers with `USB_MIXER_BESPOKEN`.

## Risks and Test Signals
Risks include protocol deadlock if ACKs are lost, reinit races around suspend, user-space ABI mistakes, label TLV access before meter control setup, notification URB resubmit failures, and insufficient command validation for destructive vendor commands. Test signals include hwdep open permission checks, init/cmd/read/poll behavior with fcp-server, meter map bounds, label TLV add/remove notifications, suspend/resume reinit, disconnect during blocked read or command, and malformed response sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/fcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/fcp.h -->
# sources/distributed-fs/ceph-client/sound/usb/fcp.h

## Purpose
Declares the Focusrite Control Protocol integration point for USB mixer setup.

## API and Integration
`snd_fcp_init(struct usb_mixer_interface *mixer)` initializes private protocol state, discovers the Focusrite vendor interface, and registers the hwdep device when applicable. The caller must provide a mixer with a valid `chip`, protocol, and mixer lifetime hooks.

## State, Dependencies, and Risks
State is allocated by `fcp.c` and attached to `mixer->private_data`; this header only exposes the entry point. Risk centers on calling it for unsupported or non-UAC2 mixer contexts, though `fcp.c` exits early for missing protocol and validates the vendor-specific interface.

## Test Signals
Build coverage plus probing Focusrite and non-Focusrite devices validates correct no-op and initialization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/fcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/format.c -->
# sources/distributed-fs/ceph-client/sound/usb/format.c

## Purpose
Parses USB Audio Class format descriptors into ALSA `audioformat` capabilities. It maps UAC type I/II/III formats to ALSA PCM format bits, builds sample-rate tables for UAC1 and UAC2/UAC3, applies device-specific rate and DSD quirks, and rejects unusable descriptors.

## Important APIs and Functions
Public functions are `snd_usb_parse_audio_format()` for UAC1/UAC2 format descriptors and `snd_usb_parse_audio_format_v3()` for UAC3 AS headers. Core helpers include `parse_audio_format_i_type()`, `parse_audio_format_rates_v1()`, `parse_uac2_sample_rate_range()`, `parse_audio_format_rates_v2v3()`, `validate_sample_rate_table_v2v3()`, `parse_audio_format_i()`, and `parse_audio_format_ii()`.

## Control Flow
For type I/III, parsing determines sample width/subslot size from protocol-specific descriptors, converts UAC format bits to ALSA formats, applies endian and DSD quirks, then parses rates. UAC1 reads discrete or continuous rates from descriptor triplets. UAC2/UAC3 resolves the clock source, issues `UAC2_CS_RANGE` requests, parses min/max/resolution triplets, optionally allocates a rate table, filters known-bad Presonus and Focusrite altsetting rates, validates altsettings for quirked devices by setting sample rates and querying `VAL_ALT_SETTINGS`, and computes rate bitmasks/min/max. Type II maps AC3/MPEG-like streams and parses rates similarly. UAC3 infers type I vs type III from AS `bmFormats`.

## State and Persistence
The function mutates the caller-provided `audioformat`: `formats`, `fmt_type`, `fmt_bits`, `fmt_sz`, `channels`, `frame_size`, `rate_table`, `nr_rates`, `rate_min`, `rate_max`, `rates`, and DSD flags. It allocates `rate_table` memory owned by the format object. Device state may be temporarily changed by validation via clock sample-rate writes and interface altsetting reset.

## Dependencies and Integration
Depends on USB audio descriptors, ALSA PCM format/rate helpers, `clock.c` for source/rate queries, `helper.c` for descriptor lookup, and quirk helpers for endian and DSD handling. Parsed formats feed PCM hw constraints, endpoint setup, and implicit feedback matching.

## Risks and Test Signals
Risks include malformed descriptor lengths, rate-table allocation leaks on repeated parsing, validation side effects on devices that misbehave after rate probes, infinite rate loops if resolution is zero, and hard-coded device filters becoming stale. Test with UAC1 discrete/continuous rates, UAC2 range descriptors, UAC3 BADD/generic formats, Focusrite multi-altsetting devices, Presonus Studio devices, Line 6/Rode fixed-rate quirks, DSD raw/DoP paths, and fuzzed descriptor buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/format.h -->
# sources/distributed-fs/ceph-client/sound/usb/format.h

## Purpose
Declares USB-audio format parsing entry points.

## APIs and Integration
`snd_usb_parse_audio_format()` parses a UAC1/UAC2 format descriptor and fills an `audioformat`. `snd_usb_parse_audio_format_v3()` parses a UAC3 AS header and fills the same model. These functions are consumed by stream discovery code outside this subset before PCM devices and endpoint constraints are created.

## State, Dependencies, and Risks
The caller owns the `audioformat` object and any lifetime for allocated rate tables. Callers must pass descriptor pointers validated enough for the implementation’s protocol-specific casts. Incorrect `stream` or partially initialized `fp` fields can produce wrong endpoint/rate capability data.

## Test Signals
Build coverage and enumeration of UAC1, UAC2, and UAC3 devices detect API drift. Descriptor parsing tests should confirm that output `audioformat` fields match expected ALSA constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/helper.c -->
# sources/distributed-fs/ceph-client/sound/usb/helper.c

## Purpose
Provides shared utility functions for USB-audio descriptor scanning, endian byte combining, safe control transfers, data interval parsing, and streaming-to-control-interface mapping.

## Important APIs and Functions
`snd_usb_combine_bytes()` combines 1-4 little-endian bytes. `snd_usb_find_desc()` walks descriptor blobs safely using `bLength`; `snd_usb_find_csint_desc()` filters class-specific interface descriptors by subtype and is exported. `snd_usb_ctl_msg()` wraps `usb_control_msg()` with a heap buffer to avoid DMA to stack and applies post-transfer quirks. `snd_usb_parse_datainterval()` maps high/super-speed endpoint interval to data interval. `snd_usb_get_host_interface()`, `snd_usb_add_ctrl_interface_link()`, and `snd_usb_find_ctrl_interface()` locate altsettings and associated control interfaces.

## Control Flow
Descriptor walking starts at `descstart`, rejects descriptors shorter than two bytes or beyond buffer end, and returns the first requested type after an optional pointer. Control transfers allocate/copy a temporary buffer, choose GET or SET timeout by direction, call the USB core, copy results back for nonzero sizes, free the buffer, and invoke quirk fixups. Control-interface mapping appends explicit interface-to-control-interface links and falls back to `chip->ctrl_intf`.

## State and Persistence
The only persistent driver state modified here is `chip->intf_to_ctrl[]` and `chip->num_intf_to_ctrl`. Control transfers mutate device state depending on request; no filesystem state exists.

## Dependencies and Integration
Used by clock, format, fcp, endpoint, and other USB-audio modules. Depends on Linux USB core APIs, local `usbaudio.h`, `quirks.h`, and descriptor macros from `helper.h`.

## Risks and Test Signals
Risks include NULL `usb_ifnum_to_if()` dereference in `snd_usb_add_ctrl_interface_link()` if called with invalid control interface, partial copy behavior when `usb_control_msg()` returns an error after DMA buffer changes, and descriptor scans stopping at malformed data. Test signals include descriptor-fuzz enumeration, control transfer error injection, devices with multiple audio-control interfaces, high-speed interval parsing, and quirk-modified control responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/helper.h -->
# sources/distributed-fs/ceph-client/sound/usb/helper.h

## Purpose
Declares common USB-audio helper APIs and descriptor accessor macros.

## APIs and Integration
It exposes byte combining, descriptor lookup, safe control messaging, data interval parsing, host-interface lookup, control-interface link management, and descriptor validation declarations implemented elsewhere. Macros such as `get_iface_desc()`, `get_endpoint()`, `get_ep_desc()`, `get_cfg_desc()`, and `snd_usb_get_speed()` abstract USB structure access used throughout the driver.

## State, Dependencies, and Risks
The header depends on Linux USB and local `struct snd_usb_audio` types. Accessor macros assume valid pointers and endpoint indexes; callers must validate descriptor counts before use. `snd_usb_ctrl_intf()` assumes a non-NULL control host interface.

## Test Signals
Build coverage across USB-audio modules and runtime enumeration of devices with malformed descriptors or multiple control interfaces exercise this API surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/hiface/Makefile

## Purpose
Builds the standalone M2Tech hiFace-compatible USB-SPDIF ALSA driver.

## Build Integration
`snd-usb-hiface-y := chip.o pcm.o` links the probe/card layer and PCM streaming layer into one module object. `obj-$(CONFIG_SND_USB_HIFACE) += snd-usb-hiface.o` includes it when the Kconfig symbol is enabled.

## Dependencies and Risks
The Makefile assumes `chip.c` and `pcm.c` jointly provide all module entry points. Risks are straightforward build drift if a new source file is added but not listed, or if `CONFIG_SND_USB_HIFACE` is renamed.

## Test Signals
Kernel build with `CONFIG_SND_USB_HIFACE=m` or `y` confirms object composition; module load/probe tests confirm runtime linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/chip.c -->
# sources/distributed-fs/ceph-client/sound/usb/hiface/chip.c

## Purpose
Implements USB driver registration, ALSA card creation, probe, disconnect, and device ID quirks for M2Tech hiFace-compatible USB-SPDIF devices.

## Important APIs and Functions
The module exposes a `usb_driver` through `module_usb_driver()`. `hiface_chip_probe()` sets interface 0 altsetting 0, finds an enabled ALSA card slot, creates the card, initializes PCM via `hiface_pcm_init()`, registers the card, and stores interface data. `hiface_chip_disconnect()` disconnects the ALSA card, aborts PCM, and frees when closed. `hiface_chip_create()` fills ALSA card driver/shortname/longname and initializes `struct hiface_chip`.

## Control Flow and State
Probe is serialized by `register_mutex` while selecting an enabled index. Vendor-specific `driver_info` provides user-facing device names and an `extra_freq` flag for 352.8/384 kHz support. Disconnect prevents new user-space operations with `snd_card_disconnect()`, stops USB playback through `hiface_pcm_abort()`, then defers free until open handles close.

## Dependencies and Integration
Depends on ALSA card APIs, Linux USB module/device tables, `chip.h`, and `pcm.h`. The device table covers many vendor/product IDs that share the hiFace protocol.

## Risks and Test Signals
Risks include simplistic card-slot selection that does not mark slots consumed in this file, errors after `snd_card_new()` requiring correct cleanup, and device table quirk mistakes. Tests should cover probing multiple matching devices, disabled module slots, extra-frequency devices, disconnect during playback, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/chip.h -->
# sources/distributed-fs/ceph-client/sound/usb/hiface/chip.h

## Purpose
Defines the shared hiFace chip object used by the probe and PCM layers.

## Types and Integration
`struct hiface_chip` stores the USB device pointer, ALSA card pointer, and private `pcm_runtime` pointer. `pcm_runtime` is forward-declared so `chip.c` does not need PCM internals. `pcm.c` owns allocation and teardown of `chip->pcm`.

## State and Risks
The struct is embedded in ALSA card private data. Lifetime is tied to `snd_card_new()`/`snd_card_free_when_closed()`. Risks are stale `chip->pcm` on partial PCM initialization failure or disconnect while callbacks still reference the chip; `hiface_pcm_abort()` and card disconnect mitigate this.

## Test Signals
Compile coverage plus probe/disconnect/playback tests validate that both layers agree on the shared structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.c

## Purpose
Implements playback-only ALSA PCM support for hiFace-compatible USB-SPDIF devices using bulk OUT URBs and vendor sample-rate requests.

## Important APIs, Types, and Functions
`hiface_pcm_init()` allocates runtime state, creates eight bulk OUT URBs, creates an ALSA playback PCM, installs callbacks, and attaches runtime to `chip->pcm`. `hiface_pcm_abort()` sets a panic flag and stops streaming. Internal types `pcm_runtime`, `pcm_substream`, and `pcm_urb` track stream state, URB buffers, active playback substream, DMA offsets, and period offsets. PCM callbacks are `hiface_pcm_open()`, `close()`, `prepare()`, `trigger()`, and `pointer()`.

## Control Flow
Open installs hardware constraints; `extra_freq` devices add KNOT rate constraints up to 384 kHz. Prepare stops any previous stream, resets offsets, sends a vendor control request for the selected rate, and starts the URB ring. Startup submits zeroed URBs and waits up to one second for the first completion to prove the stream is running. Completion copies ALSA ring-buffer data into the URB with half-word-swapped 32-bit samples when active, sends silence when inactive, reports period elapsed outside the spinlocked copy region, and resubmits. Trigger only toggles `sub->active`; streaming remains primed from prepare. Close stops stream and clears the substream.

## State and Persistence
State is volatile: `stream_state`, `panic`, `active`, DMA/period offsets, anchored URBs, and `extra_freq`. The selected sample rate is device-visible after a vendor request but not persisted by the driver.

## Dependencies and Integration
Depends on ALSA PCM APIs, Linux USB bulk URBs/control messages, and `hiface_chip`. It is independent from the generic USB-audio endpoint engine.

## Risks and Test Signals
Risks include panic state becoming sticky after one URB failure until stream restart, period comparison using bytes against `runtime->period_size` frames, no capture support, rate request without ACK, URB buffer cleanup after partial init, and disconnect races with completion callbacks. Tests should play all supported rates, validate 352.8/384 kHz only on extra-frequency devices, inspect sample word order, run pause/start/stop cycles, disconnect during playback, and run USB error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.h

## Purpose
Declares the hiFace PCM layer entry points used by the USB probe/disconnect layer.

## APIs and Integration
`hiface_pcm_init(struct hiface_chip *chip, u8 extra_freq)` creates ALSA playback PCM state and URBs. `hiface_pcm_abort(struct hiface_chip *chip)` stops streaming and prevents further PCM work after disconnect or fatal errors.

## State, Dependencies, and Risks
The implementation stores runtime state in `chip->pcm`; callers must pass a valid `hiface_chip` with a live USB device and ALSA card. Abort must be safe during disconnect and while callbacks are outstanding.

## Test Signals
Build coverage and probe/disconnect/playback tests validate the public contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/hiface/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/implicit.c -->
# sources/distributed-fs/ceph-client/sound/usb/implicit.c

## Purpose
Detects and configures implicit feedback synchronization for USB-audio formats, including generic UAC2 cases and vendor-specific quirks. It also selects a matching sync audioformat for implicit-feedback endpoints during PCM setup.

## Important APIs and Functions
`snd_usb_parse_implicit_fb_quirk()` mutates an `audioformat` to add sync endpoint/interface/altsetting fields when a quirk or generic rule applies. `snd_usb_find_implicit_fb_sync_format()` finds the best matching format for the sync endpoint. Helpers add fixed or generic sync endpoints, handle Roland/BOSS and Pioneer layouts, and score candidate formats by rate/format/channels.

## Control Flow
For playback endpoints, the parser first checks explicit quirk tables, then generic UAC2 implicit feedback, Roland/BOSS vendor-class pairs, Pioneer shared-altsetting layouts, and optional generic implicit feedback flags. For capture endpoints, only fixed capture quirks and Roland full-duplex support are handled; Pioneer capture skips generic handling. Adding a sync endpoint records endpoint number, interface, altsetting, endpoint index, and sets `fmt->implicit_fb`. Later, sync-format selection optionally falls back to the target when the same altsetting is shared, searches `chip->pcm_list` for a substream with matching endpoint and format type, and scores formats compatible with requested hw params.

## State and Persistence
State changes are confined to `audioformat` fields and sometimes `chip->quirk_flags` such as `QUIRK_FLAG_PLAYBACK_FIRST`. No persistent storage exists.

## Dependencies and Integration
Depends on USB descriptors, `card.h`, `helper.h`, PCM fixed-rate helper, and parsed PCM stream lists. Endpoint code consumes `fmt->implicit_fb` and sync fields to link endpoints and drive packet sizes from capture feedback.

## Risks and Test Signals
Risks include incorrect endpoint/interface assumptions for vendor-specific devices, missing capture quirk table entries, shared-altsetting fallback choosing an incompatible format, and `fixed_rate` assignment when no substream is found. Tests should cover known M-Audio, MOTU, Roland/BOSS, Pioneer, Yamaha/Steinberg/Fractal/SSL/Zoom devices, generic UAC2 implicit feedback descriptors, and full-duplex open with matching/mismatched rates and channel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/implicit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/implicit.h -->
# sources/distributed-fs/ceph-client/sound/usb/implicit.h

## Purpose
Declares implicit-feedback detection and sync-format selection APIs.

## APIs and Integration
`snd_usb_parse_implicit_fb_quirk()` is called during format discovery to annotate an `audioformat` with implicit sync endpoint details. `snd_usb_find_implicit_fb_sync_format()` is called during PCM setup to find a compatible sync-side `audioformat` for selected hw params and to report fixed-rate behavior.

## State, Dependencies, and Risks
Callers must pass initialized USB-audio chip, format, descriptors, and hw params. The implementation mutates format state and may set quirk flags. Misuse can produce unlinked or incorrectly linked sync endpoints.

## Test Signals
Compile coverage and implicit-feedback full-duplex playback/capture tests validate the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/implicit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/Kconfig -->
# sources/distributed-fs/ceph-client/sound/usb/line6/Kconfig

## Purpose
Defines kernel configuration symbols for the shared Line 6 USB support layer and the POD, PODHD, TonePort, and Variax device drivers.

## Configuration Integration
`SND_USB_LINE6` is a hidden tristate selected by specific device drivers and selects ALSA raw MIDI, PCM, and hwdep support. `SND_USB_POD`, `SND_USB_PODHD`, `SND_USB_TONEPORT`, and `SND_USB_VARIAX` are user-visible tristates that select the shared layer. TonePort also selects LED support.

## Dependencies and Risks
The file relies on selected ALSA subsystems rather than explicit dependencies. Risks include missing selects when shared code grows new subsystem use, and user confusion because the common module is hidden.

## Test Signals
Kconfig builds for each symbol as module and built-in should verify dependency closure and object linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/line6/Makefile

## Purpose
Builds the shared Line 6 USB module and the device-specific companion modules.

## Build Integration
`snd-usb-line6-y` combines capture, driver, MIDI, MIDI buffer, PCM, and playback objects. Device-specific objects build into `snd-usb-pod`, `snd-usb-podhd`, `snd-usb-toneport`, and `snd-usb-variax`. `obj-$(CONFIG_...)` lines connect objects to the Kconfig symbols.

## Dependencies and Risks
The shared object list must stay in sync with exported functions used by device modules. Playback is included even though not part of this work item, so capture/PCM references to playback helpers depend on that object. Build drift is the main risk.

## Test Signals
Kernel builds for each Line 6 configuration and module load tests catch missing object or symbol issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/capture.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/capture.c

## Purpose
Implements Line 6 isochronous capture URB allocation, submission, completion handling, ALSA capture copying, period accounting, and capture PCM callbacks.

## Important APIs and Functions
Exports `snd_line6_capture_ops`, `line6_create_audio_in_urbs()`, `line6_submit_audio_in_all_urbs()`, `line6_capture_copy()`, and `line6_capture_check_period()`. Private `submit_audio_in_urb()` finds a free URB slot and submits it. `audio_in_callback()` processes completed capture URBs.

## Control Flow
Open applies device-specific rational rate constraints, acquires capture helper buffers, and installs capture hardware. Triggering is handled by common `snd_line6_trigger()`. URB allocation creates `line6->iso_buffers` isochronous URBs on `ep_audio_r`. Submission fills one packet descriptor per URB from `max_packet_size_in`, points transfer buffer into the shared input buffer, submits, and marks the active bit. Completion records `last_frame`, finds the URB index, copies non-empty PCM packets into ALSA DMA unless impulse mode is active, stores the previous frame for monitoring/playback synchronization, clears active/unlink bits, resubmits unless shutting down, and reports periods.

## State and Persistence
State lives in `line6pcm->in`: URB arrays, shared buffer, active/unlink masks, `pos_done`, `bytes`, `period`, `running`, and `last_frame`. `prev_fbuf`/`prev_fsize` in the parent PCM object cache the latest capture frame. No persistent storage exists.

## Dependencies and Integration
Depends on `pcm.h` stream state, common PCM helpers in `pcm.c`, device properties from `driver.h`, and playback/monitor code through `prev_fbuf`. ALSA callbacks reuse common hw_params/free/prepare/trigger/pointer functions.

## Risks and Test Signals
Risks include assuming `LINE6_ISO_PACKETS == 1`, sync issues when `iso_buffers != 2`, packet-size overruns, active bit leaks if submission fails, copying while runtime is invalid, and disconnect during callbacks. Tests should record audio at supported rates, run capture-only on devices needing playback helper, exercise impulse mode, disconnect during capture, and validate period wakeups and ring wrap copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/capture.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/capture.h

## Purpose
Declares Line 6 capture callbacks and helper functions.

## APIs and Integration
Exposes `snd_line6_capture_ops` for PCM registration, capture copy/period helpers for capture processing, and URB creation/submission functions used by `pcm.c` stream startup and initialization.

## State, Dependencies, and Risks
All APIs operate on `struct snd_line6_pcm`, whose stream fields must already be initialized. Callers must hold `line6pcm->in.lock` for submission paths as documented in the implementation.

## Test Signals
Build coverage and capture stream start/stop tests validate header contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/driver.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/driver.c

## Purpose
Provides the shared Line 6 USB driver core: probe/disconnect/PM scaffolding, control endpoint listening, raw synchronous/asynchronous message transmission, device memory read/write helpers, hwdep buffering for non-MIDI control devices, MIDI manufacturer constants, and startup work dispatch.

## Important APIs and Functions
Exports `line6_probe()`, `line6_disconnect()`, PM helpers, `line6_send_raw_message()`, `line6_send_raw_message_async()`, `line6_send_sysex_message()`, `line6_alloc_sysex_buffer()`, `line6_version_request_async()`, `line6_read_data()`, `line6_write_data()`, and `line6_read_serial_number()`. `line6_start_listen()` and `line6_data_received()` own the receive URB loop. `line6_hwdep_init()` creates the config hwdep path for non-MIDI control.

## Control Flow
Probe creates an ALSA card with device-specific private size, stores shared properties, claims a USB device ref, sets the configured altsetting, derives endpoint interval/max packet/iso-buffer properties, initializes control support if requested, calls the device-specific private initializer, and leaves registration to that path. Incoming control data is read through an interrupt or bulk URB depending on capabilities; MIDI-control devices feed `midibuf_in`, parse complete MIDI messages, pass raw MIDI to ALSA, and call optional device processing. Non-MIDI devices expose the raw messages through an exclusive hwdep FIFO. Raw sends fragment by `max_packet_size`; async sends chain one URB through completion callbacks. Read/write data helpers use vendor control request `0x67` with status polling. Disconnect cancels startup work, kills listen URB, disconnects ALSA card, stops PCM, calls device-specific disconnect, clears interface data, and frees the card when closed.

## State and Persistence
`struct usb_line6` stores USB/card pointers, endpoint properties, listen URB/buffers, message FIFO state, delayed startup work, and device callbacks. Device memory reads/writes affect hardware state; driver-side state is volatile. The hwdep FIFO buffers only while opened.

## Dependencies and Integration
Depends on ALSA core/hwdep, Linux USB, MIDI and PCM Line 6 modules, and device-specific modules that pass `line6_properties` and private init callbacks. Shared exported functions are used by POD/TonePort/Variax modules.

## Risks and Test Signals
Risks include async send lifetime of caller-provided buffers, listener resubmission after non-ESHUTDOWN errors without checking shutdown broadly, FIFO overflow silently dropping hwdep messages, polling loops blocking for device status, and disconnect races with pending async URBs. Tests should cover MIDI and non-MIDI control devices, large fragmented sends, hwdep nonblocking reads/writes, serial read/write helpers, suspend/resume listener restart, and disconnect during active control and PCM traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/driver.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/driver.h

## Purpose
Defines the shared Line 6 driver data model, constants, capability bits, and exported core APIs.

## Important Types and APIs
`struct line6_properties` describes device identity, capabilities, altsetting, control endpoints, and audio endpoints. Capability bits distinguish control, PCM, hardware monitoring, capture requiring output, MIDI-over-control, low-level info, and monitoring controls. `struct usb_line6` is the shared per-card state: USB device, properties, packet timing, ALSA card, PCM/MIDI objects, listen URB/buffers, message FIFO, startup work, and callback hooks. The header declares raw message, sysex, read/write, serial number, probe/disconnect, and PM APIs.

## State and Integration
Device-specific modules embed `struct usb_line6` as the leading portion of larger private structs by passing a `data_size` to `line6_probe()`. PCM and MIDI modules hang their state off `line6pcm` and `line6midi`. The FIFO and delayed work provide optional control/event plumbing.

## Risks and Test Signals
Risks include capability combinations that require matching endpoints and initialized submodules, size/layout assumptions for embedding, and fallback packet properties hiding endpoint descriptor bugs. Tests should instantiate each device-specific property set and verify probe, control, PCM, and MIDI combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/midi.c

## Purpose
Implements the ALSA raw MIDI interface for Line 6 devices that transport control data as MIDI over USB interrupt endpoints.

## Important APIs and Functions
`line6_init_midi()` creates a duplex rawmidi device and initializes input/output `midi_buffer` objects. `line6_midi_receive()` forwards parsed incoming MIDI bytes to the active ALSA input substream. `line6_midi_transmit()` drains ALSA rawmidi output into the MIDI buffer and submits complete chunks asynchronously. `send_midi_async()` allocates one interrupt URB per outgoing MIDI chunk, and `midi_sent()` frees it and continues draining.

## Control Flow
Output trigger stores the transmit substream, takes the MIDI spinlock, and starts transmission only when no send URBs are active. Transmission peeks from ALSA, writes into `midibuf_out`, acknowledges bytes, reads complete/splittable MIDI messages, and sends them asynchronously. Completion decrements `num_active_send_urbs`; if it reaches zero, it tries to transmit more and wakes drain waiters if still idle. Input trigger sets or clears the receive substream; incoming parsed data from `driver.c` calls `line6_midi_receive()`.

## State and Persistence
`struct snd_line6_midi` stores active input/output substreams, active send URB count, spinlock, waitqueue, and MIDI buffers. State exists only while the rawmidi device/card exists.

## Dependencies and Integration
Depends on ALSA rawmidi, USB interrupt URBs, `driver.h` endpoint properties, and `midibuf.c` message framing. `driver.c` initializes MIDI only for `LINE6_CAP_CONTROL_MIDI` and feeds received data.

## Risks and Test Signals
Risks include URB transfer buffer leak on `usb_urb_ep_type_check()`/submit failure because the error path frees the URB but not the duplicated transfer buffer, async sends after disconnect, and lock-held calls that may enqueue many URBs. Tests should cover MIDI input/output, running status, drain waits, endpoint validation failure injection, disconnect during active sends, and buffer overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midi.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/midi.h

## Purpose
Declares the Line 6 raw MIDI state object and MIDI initialization/receive APIs.

## Types and APIs
`struct snd_line6_midi` links back to `usb_line6`, tracks active rawmidi receive/transmit substreams, counts active send URBs, protects buffers with a spinlock, provides a send waitqueue, and owns input/output `midi_buffer` instances. `line6_init_midi()` creates rawmidi state and `line6_midi_receive()` forwards incoming MIDI data.

## State, Dependencies, and Risks
The header depends on ALSA rawmidi and `midibuf.h`. Callers must initialize MIDI only for devices with MIDI control capability and must not call receive before `line6->line6midi` is set.

## Test Signals
Build coverage and rawmidi open/trigger/input/output tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.c

## Purpose
Provides a small circular MIDI message buffer with MIDI message boundary detection, optional splitting for transmit, running-status support, active-sense suppression, and Line 6 receive-channel correction.

## Important APIs and Functions
Public functions initialize/reset/destroy buffers, report bytes free/used, write bytes, read a complete message or split chunk, and ignore bytes. `midibuf_message_length()` classifies MIDI status bytes. `line6_midibuf_read()` is the core parser and supports `LINE6_MIDIBUF_READ_TX` and `LINE6_MIDIBUF_READ_RX` modes.

## Control Flow
Writes drop a trailing active-sense byte `0xfe`, clamp to free space, and copy with wraparound. Reads require at least a three-byte destination, examine the next command, correct PODxt receive status bytes `0xb2`, `0xc2`, and `0xf2` to channel-zero status, use the current or previous status byte to determine MIDI length, search for the next status byte for variable-length data, optionally return zero until a complete message is available, copy with wraparound, inject running status when needed, and clears the full flag. Ignore advances the read pointer modulo size.

## State and Persistence
`struct midi_buffer` stores heap buffer, size, split behavior, read/write positions, full flag, and previous command. State is volatile and protected by callers, usually the MIDI spinlock.

## Dependencies and Integration
Used by `midi.c` for outgoing message framing and by `driver.c` for incoming MIDI-control message parsing. Depends only on kernel allocation and memory copy helpers.

## Risks and Test Signals
Risks include incomplete SysEx messages stalling reads when split is disabled, running-status edge cases, active-sense accounting returning more consumed bytes than stored, and caller responsibility for locking. Tests should feed status/data byte sequences, wraparound cases, running status, malformed/partial SysEx, buffer-full overflow, RX channel correction, and TX split mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.h

## Purpose
Declares the Line 6 MIDI circular buffer type and operations.

## APIs and State
`struct midi_buffer` stores buffer pointer, size, split mode, positions, full flag, and previous command. APIs cover init, reset, destroy, bytes used/free, write, read, and ignore. Read mode constants distinguish transmit and receive behavior.

## Dependencies and Risks
The implementation assumes external synchronization and valid initialized buffers. Callers must choose split mode appropriately: receive buffers generally wait for full messages, transmit buffers can split.

## Test Signals
Unit-style tests for buffer wraparound, full/empty accounting, and MIDI message parsing validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/line6/pcm.c

## Purpose
Implements the shared Line 6 PCM control layer for playback/capture streams, stream ownership arbitration, buffer allocation, ALSA controls, PCM device creation, disconnect synchronization, and common ALSA PCM callbacks.

## Important APIs and Functions
Exports `line6_init_pcm()`, `line6_pcm_disconnect()`, `line6_pcm_acquire()`, `line6_pcm_release()`, `snd_line6_hw_params()`, `snd_line6_hw_free()`, `snd_line6_prepare()`, `snd_line6_trigger()`, and `snd_line6_pointer()`. Internal helpers manage URB unlink/wait, per-direction stream start/stop, and buffer acquire/release. ALSA controls include PCM playback volume and impulse response volume/period.

## Control Flow
Initialization creates a duplex PCM, allocates `snd_line6_pcm`, initializes locks/default volumes/impulse period, derives max isochronous packet sizes, creates playback and capture URBs, and registers mixer controls. `hw_params` allocates the per-stream shared buffer and records the period size; `hw_free` releases it when no other stream type owns it. `prepare` waits for outstanding URBs when not running and resets both directions once per prepare cycle. `trigger` operates on grouped substreams: start/resume may also start a playback helper for capture devices needing output, while stop/suspend clears running flags and unlinks URBs once no stream type remains. Monitor/impulse users call `line6_pcm_acquire()` to allocate both directions and optionally start them; release stops and frees both directions for that type. Disconnect unlinks and waits for both directions.

## State and Persistence
`snd_line6_pcm` stores per-direction stream state, shared buffers, active/unlink bitmasks, positions, periods, volume controls, impulse parameters, previous capture frame, packet sizes, and flags. State is volatile. ALSA mixer values persist only for the lifetime of the card instance.

## Dependencies and Integration
Depends on ALSA PCM/control APIs, Linux USB, `capture.c`, playback helpers from `playback.c`, and device properties from `driver.h`. Device-specific modules pass `line6_pcm_properties` with hardware constraints.

## Risks and Test Signals
Risks include stream ownership bitmask mistakes, freeing buffers while URBs are still active, grouped trigger ordering across playback/capture, capture-helper playback not stopping, active URB timeout, and interactions between impulse/monitor/PCM users. Tests should cover duplex playback/capture, capture on `LINE6_CAP_IN_NEEDS_OUT` devices, grouped ALSA triggers, hw_params/free cycles, impulse controls, monitor users, disconnect while running, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/line6/pcm.h

## Purpose
Defines Line 6 PCM stream constants, state structures, properties, and common PCM APIs shared by capture, playback, and device-specific modules.

## Important Types and APIs
`LINE6_ISO_PACKETS`, `LINE6_ISO_INTERVAL`, and `LINE6_IMPULSE_DEFAULT_PERIOD` define transfer cadence and default impulse behavior. Stream type bits distinguish ALSA PCM, monitor, impulse, and capture-helper ownership. `struct line6_pcm_properties` holds ALSA hardware constraints and bytes per channel. `struct line6_pcm_stream` tracks URBs, shared buffer, positions, period accounting, active/unlink masks, locks, opened/running bitmasks, and last frame. `struct snd_line6_pcm` owns duplex streams, packet sizes, volumes, impulse state, flags, and backpointer to `usb_line6`. Declared APIs cover initialization, acquire/release, disconnect, common PCM callbacks, and stream pointer/trigger handling.

## State and Integration
The header is the contract between `pcm.c`, `capture.c`, playback code, and device modules. Device modules supply properties; common PCM code creates runtime state; capture/playback URB callbacks update positions and active masks under spinlocks.

## Risks and Test Signals
Risks include assumptions that ALSA stream enum values match direction loop indexes, bitmask state becoming inconsistent across multiple stream users, and fixed `LINE6_ISO_PACKETS == 1` assumptions in capture. Tests should validate all stream-owner combinations, duplex operation, period accounting, and high-speed vs full-speed iso buffer counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/line6/pcm.h -->
