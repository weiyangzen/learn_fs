# subset-b-006565 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.c -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.c

Purpose: Tascam US-16x08 device-specific mixer support for ALSA usb-audio. It creates mixer controls for line routing, master/channel faders, mute/phase/pan, EQ, compressor settings, DSP bypass, bus output, and meter polling using vendor USB control messages.

Important APIs, types, and functions: exports `snd_us16x08_controls_create()`. The implementation uses `struct usb_mixer_elem_info`, ALSA `struct snd_kcontrol_new` templates, vendor message templates such as `route_msg`, `mix_msg_in`, `mix_msg_out`, `comp_msg`, and `eqs_msq`, and private stores `snd_us16x08_eq_store`, `snd_us16x08_comp_store`, and `snd_us16x08_meter_store` from the header. `add_new_ctl()` is the common control allocator; `snd_us16x08_send_urb()` and `snd_us16x08_recv_urb()` wrap the vendor control transfers.

Control flow: `snd_us16x08_controls_create()` only acts on interface number 3, adds route controls, allocates shared compressor state, creates master and per-channel controls with initialized cache values, allocates EQ state, creates EQ and compressor controls, then creates a meter control whose store points back to the compressor store. Put handlers validate user values, translate ALSA-visible biased ranges into device values, write the appropriate bytes into a vendor message template, send the control transfer, and update the ALSA cache on success. EQ switch changes send all four bands with sleeps between messages. Meter get cycles through four polling phases, parses six ten-byte status records from each response, and optionally asks for compressor reduction levels for a selected or rotating channel.

State and persistence: state is in ALSA control caches plus shared heap stores attached to controls; it is not read back wholesale from hardware on load. `elem_private_free()` frees a shared EQ/compressor/meter store only from the one designated control, while other controls hold non-owning pointers. Meter phase is kept in `kcontrol->private_value`, so reads have side effects. Device state persists in the hardware until reset or changed by another host path.

Dependencies and integration points: depends on usb-audio mixer infrastructure, `snd_usb_ctl_msg()`, ALSA control callbacks, and the US-16x08 vendor protocol constants in `mixer_us16x08.h`. It is invoked from the generic mixer parser for the matching device/interface.

Risks: several put handlers return `1` even after a failed send path, which can make userspace believe a value changed. Shared private stores rely on creation order and single-owner cleanup; partial failures after allocating stores can leak until card teardown or leave later controls uncreated. Meter polling mutates `private_value` and shared meter fields, so concurrent mixer reads can observe interleaved polling state. The vendor message offsets are hard-coded and fragile against firmware changes.

Test signals: `amixer controls` should show US-16x08 route, line, EQ, compressor, master, and meter controls; setting each control should produce successful vendor control transfers and cache updates; meter reads should update 16 input levels, two master levels, and compressor reduction levels; removal should free controls without double-freeing shared stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.h -->
# sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.h

Purpose: private interface and constants for the Tascam US-16x08 mixer extension.

Important APIs, types, and data: declares `snd_us16x08_controls_create()`. It defines channel count, ALSA range bias constants, packed `kcontrol->private_value` accessors (`SND_US16X08_KCSET`, `SND_US16X08_KCBIAS`, `SND_US16X08_KCSTEP`, `SND_US16X08_KCMIN`, `SND_US16X08_KCMAX`), vendor control request IDs, meter response access macros, control IDs, EQ/compressor indexing helpers, and the private store structures for EQ, compressor, meter, and control creation parameters.

Control flow: the header is consumed by `mixer_us16x08.c`; its macros encode how ALSA controls map to vendor protocol IDs and how compact private values are unpacked in info/put callbacks.

State and persistence: it defines in-memory state shapes only. `snd_us16x08_eq_store` stores four parameters across four EQ bands for sixteen channels. `snd_us16x08_comp_store` stores six compressor parameters for sixteen channels. `snd_us16x08_meter_store` tracks live meter levels, compressor reduction levels, polling indices, and a pointer to the compressor store.

Dependencies and integration points: depends on usb-audio mixer types and ALSA control types included by users. `snd_us16x08_switch_info` aliases `snd_ctl_boolean_mono_info`, so the C file can use the same info callback signature as normal ALSA controls.

Risks: the packed private value format is limited to 8-bit fields, so ranges beyond 255 cannot be represented. Meter parsing macros assume fixed ten-byte records and fixed byte offsets. Store index macros rely on control IDs being arranged exactly as defined.

Test signals: compile coverage from `mixer_us16x08.c`, correct ALSA min/max/step reporting from packed private values, and static checks that all store index calculations stay within the declared array dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/mixer_us16x08.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/pcm.c -->
# sources/distributed-fs/ceph-client/sound/usb/pcm.c

Purpose: core ALSA PCM implementation for usb-audio streams. It negotiates USB audio formats, opens and configures data/sync endpoints, applies hardware constraints, handles runtime PM and UAC3 power domains, moves audio samples between ALSA ring buffers and USB URBs, and provides playback/capture PCM callbacks.

Important APIs, types, and functions: exports `snd_usb_find_format()`, `snd_usb_find_substream_format()`, `snd_usb_hw_params()`, `snd_usb_hw_free()`, `snd_usb_set_pcm_ops()`, and `snd_usb_preallocate_buffer()`. Major internals include `snd_usb_pcm_open/close/prepare`, `snd_usb_substream_playback_trigger()`, `snd_usb_substream_capture_trigger()`, `prepare_playback_urb()`, `retire_playback_urb()`, `retire_capture_urb()`, `setup_hw_info()`, hardware rule callbacks, pitch initialization, sync endpoint discovery, and endpoint start/stop helpers.

Control flow: open marks the substream busy, initializes runtime hardware limits, resumes the device, and initializes the media stream. `hw_params` starts the media pipeline, finds the exact format, resolves implicit feedback sync format if needed, powers UAC3 domains to D0, opens compatible data and sync endpoints, records `cur_audiofmt`, and programs endpoint parameters. Prepare powers the stream to D0, prepares endpoints, resets buffer pointers and DSD-over-PCM state, and starts non-low-latency playback endpoints early. Trigger installs endpoint callbacks and starts/stops endpoint scheduling. Capture completion copies URB payloads into the ALSA ring and reports periods. Playback preparation packetizes ALSA buffer data into URBs, including DSD DoP/bit-reversal and a transfer-length quirk path, while retirement updates in-flight delay.

State and persistence: substream state includes `opened`, `running`, endpoint pointers, current format, hw pointer counters, in-flight bytes, low-latency flag, DSD DoP counters, and endpoint-start bits. Runtime PM references are acquired on open and released on close. UAC3 power-domain state is driven to D0 for active streams, D1 on close/resume, and D2 on suspend.

Dependencies and integration points: integrates ALSA PCM ops, usbcore frame counters and control transfers, usb-audio endpoint/clock/implicit-feedback/media/power helpers, format quirks, and optional platform offload callers that reuse `snd_usb_hw_params()` and `snd_usb_hw_free()`.

Risks: format selection must respect shared endpoints already in use; implicit feedback couples period size and period count between paired streams. Low-latency playback depends on application pointer sync and can underfill if free-wheeling mode changes late. Many paths are protected by chip mutex, shutdown lock, or spinlock; regressions can cause races during disconnect, suspend, or trigger. URB packetization handles buffer wrapping and quirks manually, so off-by-one errors affect audio corruption or XRUN behavior.

Test signals: ALSA playback/capture at every advertised format/rate/channel combination; implicit feedback full-duplex streams with matching period constraints; suspend/resume power-domain transitions; low-latency playback start/ack behavior; DSD DoP and bit-reversed devices; disconnect during open/hw_params/trigger; `/proc/asound` stream status and endpoint frequency while running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/pcm.h -->
# sources/distributed-fs/ceph-client/sound/usb/pcm.h

Purpose: internal usb-audio PCM interface used by the card, endpoint, offload, and stream setup code.

Important APIs, types, and functions: declares PCM ops installation, suspend/resume helpers, fixed-rate detection, pitch setup, buffer preallocation, sync endpoint parsing, format lookup, and exported hardware setup/free functions. Key callers can use `snd_usb_find_format()` or `snd_usb_find_substream_format()` for matching `struct audioformat` entries and can call `snd_usb_hw_params()`/`snd_usb_hw_free()` without going through a userspace PCM substream callback.

Control flow: the header separates generic usb-audio stream setup from both ALSA PCM callbacks and platform/offload integrations. Offload code in `qcom/qc_audio_offload.c` directly builds `snd_pcm_hw_params` and then calls the declared `snd_usb_hw_params()` and `snd_usb_hw_free()`.

State and persistence: no state is defined here, but the prototypes operate on `struct snd_usb_stream`, `struct snd_usb_substream`, `struct snd_usb_audio`, and `struct audioformat` instances maintained by the usb-audio core.

Dependencies and integration points: depends on declarations from `usbaudio.h`, ALSA PCM parameter types, and the audioformat model. It is an internal contract for files in `sound/usb` and for optional platform helpers compiled with usb-audio.

Risks: direct callers of `snd_usb_hw_params()` must pair with `snd_usb_hw_free()` and handle runtime PM/opened state consistently with normal PCM callbacks. Format lookup with `strict_match=false` can return a format that still needs later constraints.

Test signals: successful build of core usb-audio and Qualcomm offload, external symbol resolution for GPL exports, and offload paths that configure and release endpoints without opening an ALSA userspace PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/power.c -->
# sources/distributed-fs/ceph-client/sound/usb/power.c

Purpose: UAC3 power-domain discovery and state management for usb-audio streams.

Important APIs, types, and functions: implements `snd_usb_find_power_domain()` and `snd_usb_power_domain_set()`. It parses `UAC3_POWER_DOMAIN` class-specific interface descriptors, allocates `struct snd_usb_power_domain`, records the domain ID, D1-to-D0 and D2-to-D0 recovery times, and sends UAC3 power-domain get/set control requests.

Control flow: `snd_usb_find_power_domain()` scans the control interface extra descriptors, validates UAC3 descriptors, and returns a newly allocated domain object when the requested entity ID appears in `baEntityID`. `snd_usb_power_domain_set()` reads the current state through a class-specific interface request, returns early if already in the requested state, otherwise writes the new state and delays after D1/D2 to D0 transitions according to descriptor recovery time.

State and persistence: the returned domain object is heap state attached elsewhere to stream/substream structures. Actual persistence is device-side power-domain state. The function does not cache current state, so each set request queries hardware first.

Dependencies and integration points: used by `pcm.c` for stream suspend/resume/open/close transitions. Depends on UAC3 descriptor definitions, descriptor validation helpers, and `snd_usb_ctl_msg()`.

Risks: invalid or missing descriptors produce no domain and silently disable this feature for a stream. D0 recovery uses `udelay(pd_rec * 50)`, so large descriptor values can busy-wait. Returning `-EINVAL` for unexpected previous state after a successful set can surprise callers even though the device was commanded.

Test signals: UAC3 devices with power-domain descriptors should transition to D0 during prepare/hw_params, D1 on close/resume, and D2 on suspend; logs should show get/set failures for broken devices; descriptor fuzzing should not read past `extra` data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/power.h -->
# sources/distributed-fs/ceph-client/sound/usb/power.h

Purpose: public internal contract for UAC3 power-domain support in usb-audio.

Important APIs, types, and data: defines `struct snd_usb_power_domain`, state constants `UAC3_PD_STATE_D0`, `UAC3_PD_STATE_D1`, and `UAC3_PD_STATE_D2`, and prototypes for `snd_usb_power_domain_set()`, `snd_usb_find_power_domain()`, `snd_usb_autoresume()`, and `snd_usb_autosuspend()`.

Control flow: stream parsing code can find a domain by entity ID, PCM code can set power states around runtime activity, and callers use autosuspend/autoresume helpers to manage USB runtime PM around ALSA open/close or offload stream setup.

State and persistence: the struct holds the power domain ID, recovery timings, and control interface pointer needed to issue later requests. It does not include locking or refcounting, so ownership is handled by the containing usb-audio objects.

Dependencies and integration points: integrates with UAC3 descriptor parsing in `power.c`, PCM lifecycle in `pcm.c`, and card-level runtime PM helpers implemented elsewhere in usb-audio.

Risks: callers must not use a domain after its control interface is gone. State constants are local enum values expected by `power.c` and should remain aligned with the UAC3 request semantics used there.

Test signals: compile users of the prototypes, runtime PM balance across open/close/offload enable/disable, and valid D0/D1/D2 requests on UAC3 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/proc.c -->
# sources/distributed-fs/ceph-client/sound/usb/proc.c

Purpose: `/proc/asound` diagnostic output for usb-audio cards and streams.

Important APIs, types, and functions: implements `snd_usb_audio_create_proc()` and `snd_usb_proc_pcm_format_add()`. Helpers print USB bus/device ID, vendor/product ID, supported PCM formats, channel counts, endpoints, sync type, rates, packet interval, bit depth, DSD flags, channel maps, sync endpoint details, running status, packet size, momentary feedback frequency, and feedback format.

Control flow: card creation calls `snd_usb_audio_create_proc()` to add `usbbus` and `usbid` read-only entries. Each PCM stream calls `snd_usb_proc_pcm_format_add()`, which creates `streamN`; reads print the card and PCM name, then playback and capture sections when those substreams have formats. Status output locks `chip->mutex` while checking running state and endpoint pointers.

State and persistence: this file creates read-only proc entries; it does not own stream state. Output reflects current `snd_usb_stream`, `snd_usb_substream`, `audioformat`, and endpoint state at read time. It suppresses bus and ID output after chip shutdown.

Dependencies and integration points: depends on ALSA info/proc APIs, usb-audio stream and endpoint structures, channel map constants, and endpoint frequency fields maintained by streaming code.

Risks: proc output is diagnostic but can still race with unusual teardown paths if callers violate locking expectations. Channel labels must stay aligned with ALSA channel-map enum values. The frequency conversion is approximate and depends on full-speed versus high-speed feedback units.

Test signals: `/proc/asound/card*/usbbus`, `usbid`, and `stream*` entries should exist; stream files should list all altsets and rates; running streams should show packet size and momentary frequency; channel maps should print labels or `--` for unknown positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/proc.h -->
# sources/distributed-fs/ceph-client/sound/usb/proc.h

Purpose: small internal header for usb-audio proc entry creation.

Important APIs, types, and functions: declares `snd_usb_audio_create_proc()` for card-level entries and `snd_usb_proc_pcm_format_add()` for per-stream diagnostics.

Control flow: card setup invokes the card-level function after `struct snd_usb_audio` exists, and stream creation invokes the PCM-format function once a `struct snd_usb_stream` and `pcm_index` are available.

State and persistence: no state is defined here. The declared functions create read-only ALSA proc entries that persist for the lifetime of the sound card.

Dependencies and integration points: depends on `struct snd_usb_audio` and `struct snd_usb_stream` definitions from usb-audio internals and on the implementation in `proc.c`.

Risks: the header exposes no cleanup API because ALSA card proc entries are lifetime-managed by the card. Callers must pass initialized card/stream objects.

Test signals: successful compilation and the presence of card-level and stream-level proc files during usb-audio device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/Makefile -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/Makefile

Purpose: Kbuild glue for the Qualcomm USB audio QMI/offload module.

Important APIs, types, and functions: no C API is defined. It builds `snd-usb-audio-qmi.o` from `usb_audio_qmi_v01.o`, `qc_audio_offload.o`, and `mixer_usb_offload.o`, and links the module when `CONFIG_SND_USB_AUDIO_QMI` is enabled.

Control flow: Kbuild compiles the generated QMI encoding tables, the offload auxiliary driver/QMI server, and the mixer controls into a single module object.

State and persistence: persistent output is the kernel object/module selected by the Kconfig symbol. Runtime state is in the C files.

Dependencies and integration points: must remain aligned with Kconfig, the auxiliary device name `q6usb.qc-usb-audio-offload`, and usb-audio platform ops registration.

Risks: omitting one object would leave either QMI encoding symbols, mixer controls, or offload ops unresolved. The module is all-or-nothing; partial feature selection is not represented here.

Test signals: `make M=sound/usb/qcom` with `CONFIG_SND_USB_AUDIO_QMI=m/y` produces `snd-usb-audio-qmi`, and symbol resolution succeeds for QMI element arrays and `snd_usb_offload_create_ctl()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.c -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.c

Purpose: ALSA read-only controls that expose Qualcomm USB audio offload routing for each playback PCM on a USB sound card.

Important APIs, types, and functions: implements `snd_usb_offload_create_ctl()`. It defines card-route and PCM-route controls whose get callbacks call `snd_soc_usb_update_offload_route()` with `SND_SOC_USB_KCTL_CARD_ROUTE` or `SND_SOC_USB_KCTL_PCM_ROUTE`. `CARD_IDX()` and `PCM_IDX()` unpack card and PCM IDs from `private_value`.

Control flow: for each playback `snd_usb_stream` with an endpoint and PCM index <= 255, `snd_usb_offload_create_ctl()` adds two card-interface controls. Each control stores the USB sound card number in the upper bits and PCM index in the lower bits, then query callbacks ask the ASoC USB backend which card/PCM currently manages the offload route. On backend errors, returned integer values are set to `-1`.

State and persistence: controls are attached to the ALSA card and are read-only. They do not cache route values; each read delegates to the backend device passed as the kcontrol chip.

Dependencies and integration points: depends on `sound/soc-usb.h`, usb-audio card and stream lists, ALSA control APIs, and the backend device supplied by `qc_audio_offload.c`.

Risks: the function mutates static `snd_kcontrol_new` templates (`name`, `count`, `private_value`) for each control creation; this is acceptable during serialized card setup but would be risky if called concurrently. Control names are stack buffers copied by `snd_ctl_new1()`, so they rely on ALSA duplicating names immediately. Only playback streams are represented.

Test signals: USB cards with offload support should show `USB Offload Playback Card Route PCM#N` and `USB Offload Playback PCM Route PCM#N`; reads should return `-1` when no route exists and backend card/PCM IDs when an ASoC offload route is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.h -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.h

Purpose: header for Qualcomm USB offload ALSA route-control creation.

Important APIs, types, and functions: declares `snd_usb_offload_create_ctl(struct snd_usb_audio *chip, struct device *bedev)`.

Control flow: `qc_audio_offload.c` calls the declared function after it identifies an offload-capable USB card and before notifying `snd_soc_usb_connect()`, allowing userspace to query the route mapping from the USB card.

State and persistence: the header defines no state. The implementation creates persistent ALSA card controls that query the supplied backend device.

Dependencies and integration points: depends on `struct snd_usb_audio` from usb-audio internals and `struct device` from the backend ASoC/auxiliary device path.

Risks: callers must pass a valid backend device with `snd_soc_usb_update_offload_route()` support; otherwise control reads return `-1`.

Test signals: compile linkage between `qc_audio_offload.o` and `mixer_usb_offload.o`, plus visible route controls on offload-capable cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/mixer_usb_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/qc_audio_offload.c -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/qc_audio_offload.c

Purpose: Qualcomm USB audio offload bridge. It registers as an auxiliary driver, exposes a QMI service to an audio DSP, hooks usb-audio platform callbacks, advertises offload-capable USB playback PCMs to ASoC, and transfers ownership of selected xHCI endpoint resources and DMA buffers to the DSP.

Important APIs, types, and functions: module driver `qc_usb_audio_offload_drv`; platform ops `offload_ops`; QMI handler `handle_uaudio_stream_req()`; setup helpers `enable_audio_stream()`, `prepare_qmi_response()`, `uaudio_endpoint_setup()`, `uaudio_event_ring_setup()`, `uaudio_transfer_buffer_setup()`, `uaudio_populate_uac_desc()`; cleanup helpers `disable_audio_stream()`, `uaudio_dev_intf_cleanup()`, `uaudio_dev_cleanup()`, `qmi_stop_session()`; state structures `uaudio_qmi_dev`, `uaudio_qmi_svc`, `uaudio_dev`, `intf_info`, and `iova_info`.

Control flow: auxiliary probe creates the QMI server, initializes IOVA pools, registers usb-audio platform ops, and rediscover devices. On USB audio connect, the driver checks for ASoC backend private data and playback PCMs, registers xHCI sideband, builds `snd_soc_usb_device`, creates offload route controls, and calls `snd_soc_usb_connect()`. A QMI stream enable request validates required TLVs and a token encoding card, PCM, and direction; marks the substream opened; builds fixed ALSA hw params; calls `snd_usb_hw_params()` and endpoint prepare; populates QMI response descriptors; registers sideband endpoints/interrupter; maps event ring, transfer rings, and transfer buffer into the backend IOMMU domain; caches per-interface cleanup state; and returns memory/resource information to the DSP. Disable requests stop/remove sideband endpoints, call `snd_usb_hw_free()`, autosuspend, unmap/free resources, and drop a kref. Disconnect, suspend, sideband ring-free, QMI bye, and QMI client disconnect all force DSP notification and cleanup.

State and persistence: global `uadev[SNDRV_CARDS]` tracks per-card USB device, chip, sideband handle, interface state, kref, and active flag. Global `uaudio_qdev` tracks the auxiliary/backend device, IOMMU IOVA pools, mapped event ring, and active card bitset. Global `uaudio_svc` tracks QMI handle and connected client address. Offload stream ownership is represented by `subs->opened`, `uadev[].in_use`, per-interface `intf_info`, and mapped IOVA list entries.

Dependencies and integration points: depends on usb-audio PCM/endpoint/power helpers, ASoC USB offload APIs, Qualcomm `q6usb_offload`, QRTR/QMI, IOMMU mapping, xHCI sideband APIs, runtime PM, and USB offload core references. It consumes QMI element arrays from `usb_audio_qmi_v01.c`.

Risks: this code has complex global state and lock ordering around `qdev_mutex` and `chip->mutex`; disconnect indication deliberately drops and reacquires both locks while waiting for DSP release. Error unwinding must match every sideband endpoint, interrupter, IOMMU map, coherent buffer, and PM reference. Token parsing trusts bit-field layout and only bounds card and format. `qc_usb_audio_probe()` does not check `qmi_handle_init()` before `qmi_add_server()`, and `qc_usb_audio_offload_fill_avail_pcms()` returns `-1` despite filling data. Static IOVA ranges are finite and fragmentation-sensitive.

Test signals: module binds to `q6usb.qc-usb-audio-offload`; QMI service appears and accepts stream enable/disable; USB card connection calls `snd_soc_usb_connect()` and creates route controls; enable responses include valid descriptors, event ring, transfer rings, buffer IOVAs, interrupter, speed, and controller; disconnect/suspend/QMI bye releases endpoints and wakes `disconnect_wq`; repeated enable/disable cycles do not leak IOVA space or coherent buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/qc_audio_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.c -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.c

Purpose: QMI encoder/decoder metadata for the Qualcomm USB audio stream service version 1.

Important APIs, types, and data: exports `qmi_uaudio_stream_req_msg_v01_ei`, `qmi_uaudio_stream_resp_msg_v01_ei`, and `qmi_uaudio_stream_ind_msg_v01_ei`. It also defines static element arrays for nested `mem_info_v01`, `apps_mem_info_v01`, `usb_endpoint_descriptor_v01`, and `usb_interface_descriptor_v01` structures.

Control flow: the QMI core uses these `struct qmi_elem_info` arrays to decode incoming stream requests, encode stream responses, and encode asynchronous device indications. Required fields use fixed TLV IDs; optional fields are represented by `QMI_OPT_FLAG` followed by a value using the same TLV type. Nested structures point at their own element arrays through `ei_array`.

State and persistence: no runtime state. The arrays are constant protocol metadata compiled into the module and shared by the QMI service in `qc_audio_offload.c`.

Dependencies and integration points: depends on `linux/soc/qcom/qmi.h` data types and the message/descriptor structures declared in `usb_audio_qmi_v01.h`. The max message length constants in the header must cover the encoded fields described here.

Risks: TLV type, offset, enum width, or optional-flag mismatches break ABI with the DSP QMI client. Because this file mirrors protocol layout manually, adding a field requires synchronized updates in the header structs, max length defines, and element arrays. Endianness is delegated to QMI data type encoders.

Test signals: QMI request decoding succeeds for valid DSP messages; response and indication encoding includes optional fields only when the matching `_valid` flag is set; ABI tests compare encoded TLV IDs and lengths against the DSP service specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.h -->
# sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.h

Purpose: protocol declarations for the Qualcomm USB audio QMI stream service.

Important APIs, types, and data: defines service ID/version and request/response/indication message IDs. It declares memory descriptors (`mem_info_v01`, `apps_mem_info_v01`), USB descriptor mirror structs, stream status/device indication/speed enums, request/response/indication message structs, max encoded message lengths, and extern QMI element arrays.

Control flow: the offload driver receives `qmi_uaudio_stream_req_msg_v01`, validates requested format/channel/rate/buffer data, and fills `qmi_uaudio_stream_resp_msg_v01` with descriptors and xHCI memory data. Disconnect/suspend paths send `qmi_uaudio_stream_ind_msg_v01` events to the DSP.

State and persistence: message structs contain transient QMI payload state. The memory info fields carry both USB-host DMA addresses and backend/sysdev IOVA addresses, with valid flags determining which optional fields are encoded.

Dependencies and integration points: consumed by `qc_audio_offload.c` and `usb_audio_qmi_v01.c`, and must match the DSP-side QMI IDL. It depends on QMI core types such as `struct qmi_elem_info` and `struct qmi_response_type_v01`.

Risks: enum min/max sentinels force signed 32-bit enum encoding and must stay compatible with QMI. Max message length constants must be updated if fields change. The protocol exposes low-level USB descriptors and IOMMU mappings, so any layout mismatch can prevent DSP offload or corrupt resource handoff.

Test signals: compile-time struct offsets used by QMI arrays, interoperability with a DSP client, successful stream request/response round trips, and indication delivery for connect/disconnect/suspend/resume events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/qcom/usb_audio_qmi_v01.h -->
