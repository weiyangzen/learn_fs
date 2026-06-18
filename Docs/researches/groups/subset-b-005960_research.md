# subset-b-005960 Research

Grouped source research for ALSA sound headers in the ceph-client source tree. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_codec.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_codec.h

Source read summary: 580 lines, legacy HD-audio codec interface layered on top of the generic `hdac_device`/`hdac_bus` core.

Purpose: defines the legacy ALSA HDA codec bus, codec driver, PCM, pin, SPDIF, GPIO, power-management, patch-loader, and DSP-loader contracts used by `sound/pci/hda` codec parsers and controller glue.

Important APIs, types, and functions: `struct hda_bus` extends `struct hdac_bus` with card, PCI, PCM-device bitmap, reset/probe/power flags, and mixer assignment state. `struct hda_codec_driver`, `struct hda_codec_ops`, `struct hda_pcm_ops`, `struct hda_pcm_stream`, `struct hda_pcm`, and `struct hda_codec` define driver callbacks, PCM stream descriptors, codec-private state, parser caches, connection lists, pin overrides, SPDIF state, jack polling, fixups, init verbs, and power accounting. Constructors and lifecycle calls include `snd_hda_codec_device_init()`, `snd_hda_codec_new()`, `snd_hda_codec_configure()`, register/unregister, and unbind cleanup. Verb helpers wrap core `snd_hdac_codec_read/write`, regmap cached writes, connection-list queries, device-select verbs, pin configuration, SPDIF assignment, PCM creation, stream setup/cleanup, GPIO, power-save, and optional patch/DSP loading.

Control flow: controller code creates an `hda_bus`, probes codec addresses, instantiates `hda_codec`, matches `hda_codec_driver` IDs, runs codec `probe`, `build_controls`, `build_pcms`, and `init`, then exposes ALSA controls/PCMs. PCM open/prepare delegates to `hda_pcm_ops`, programs stream tags and formats on converter NIDs, and cleanup tears down stream state. Runtime events arrive as unsolicited responses or jack-poll work; reset paths coordinate bus/device locks and codec reconfiguration.

State and persistence behavior: codec state is in-kernel and card-lifetime only: widget caps, pin/default overrides, connection overrides, mixer arrays, SPDIF controls, PCM refcounts, jack tables, power-on/off accounting, fixup identity, and optional user reconfiguration arrays. Hardware state persists only in codec registers until reset/suspend; this header defines caches and replay inputs for restoration.

Dependencies and integration points: depends on ALSA control/PCM/hwdep/info, generic HD-audio core, HDA verb definitions, regmap, PCI, module device IDs, runtime PM, and optional `CONFIG_SND_HDA_RECONFIG`, `CONFIG_SND_HDA_HWDEP`, patch loader, and DSP loader. It bridges codec parser modules, controller drivers, proc/hwdep diagnostics, jack reporting, and PCM stream handling.

Risks and edge cases: risks include codec lifetime races around `pcm_ref` and unbind, stale cached verbs after reset, connection-list overrides diverging from hardware topology, inconsistent pin power/shutup behavior, jack polling during suspend, and optional config stubs hiding missing DSP/patch support. Duplicated declarations/macros in this source snapshot should be treated as merge drift signals.

Test signals: validate codec probe/unbind, generic and vendor parser selection, jack unsolicited and polling paths, pin override via hwdep/reconfig, SPDIF reassignment, PCM prepare/cleanup across suspend/resume, bus reset fallback behavior, power-save accounting, and compile matrices with HDA hwdep/reconfig/DSP/patch options enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_component.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_component.h

Source read summary: 67 lines, HD-audio to DRM audio-component bridge helpers.

Purpose: declares the component interface that lets HDA audio drivers coordinate display power, wake, rate synchronization, ELD reads, and notifier registration with DRM display drivers.

Important APIs, types, and functions: `HDA_CODEC_IDX_CONTROLLER` reserves a virtual codec index for controller-level display power. When `CONFIG_SND_HDA_COMPONENT` is enabled, APIs include `snd_hdac_set_codec_wakeup()`, `snd_hdac_display_power()`, `snd_hdac_sync_audio_rate()`, `snd_hdac_acomp_get_eld()`, `snd_hdac_acomp_init()`, `snd_hdac_acomp_exit()`, and `snd_hdac_acomp_register_notifier()`. Disabled builds return success for harmless operations and `-ENODEV` for component-dependent setup/ELD/notifier calls.

Control flow: HDA HDMI/DP code initializes the audio component against a DRM master, toggles display power around codec access, asks DRM for ELD/audio-enabled state, synchronizes sample rates where supported, and unregisters at teardown.

State and persistence behavior: no independent persistent state is defined here; state lives in `hdac_bus->audio_component`, display power bitmaps, and DRM component binding. Stub paths intentionally persist nothing.

Dependencies and integration points: includes DRM audio component APIs and `hdaudio.h`. It integrates HDA codec/controller code with i915/DRM display pipelines and HDMI/DP hotplug notification.

Risks and edge cases: missing component support can silently no-op display power and wake transitions while ELD reads fail; mismatched codec indexes or unbalanced power calls can break HDMI audio on runtime PM systems.

Test signals: build with and without `CONFIG_SND_HDA_COMPONENT`, probe HDMI audio with DRM bind/unbind, verify ELD retrieval after hotplug, check display power reference balance, and exercise rate sync across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_hwdep.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_hwdep.h

Source read summary: 31 lines, userspace hwdep ioctl ABI for HD-audio verbs.

Purpose: exposes the version and ioctl payloads used by ALSA hwdep devices to issue raw HD-audio verbs and query widget capabilities.

Important APIs, types, and functions: `HDA_HWDEP_VERSION` encodes 1.0.0. `HDA_VERB(nid, verb, param)` packs NID, verb, and parameter using the documented shifts. `struct hda_verb_ioctl` carries the command and response. Ioctls are `HDA_IOCTL_PVERSION`, `HDA_IOCTL_VERB_WRITE`, and `HDA_IOCTL_GET_WCAP`.

Control flow: a userspace diagnostic or reconfiguration tool opens the codec hwdep device, packs a verb, submits ioctl, and receives the response or widget capability value from the kernel codec implementation.

State and persistence behavior: the header stores no state. Issued verbs may mutate codec hardware state; persistence is limited to hardware registers and whatever the codec driver later caches or restores.

Dependencies and integration points: relies on Linux ioctl encoding and is consumed by HD-audio hwdep implementation and tools such as codec dump/reconfig utilities.

Risks and edge cases: raw verbs can put codecs into unsupported states, ABI packing must remain stable, and 32-bit compatibility must preserve the two `u32` fields exactly.

Test signals: ioctl version checks, raw read/write verbs against a known codec, invalid NID/verb handling, compat ioctl coverage, and permission/access tests for hwdep exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_hwdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_i915.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_i915.h

Source read summary: 27 lines, Intel i915-specific HDA component wrappers.

Purpose: declares the small compatibility layer for HDA controllers that need i915 display-audio integration, especially BCLK setup and component initialization.

Important APIs, types, and functions: `snd_hdac_i915_set_bclk()` programs or derives the HDA BCLK with i915 help, `snd_hdac_i915_init()` binds to i915 when `CONFIG_SND_HDA_I915` is enabled, and `snd_hdac_i915_exit()` always forwards to `snd_hdac_acomp_exit()`. Disabled builds no-op BCLK and return `-ENODEV` for init.

Control flow: controller probe calls init, then sets BCLK before audio stream use; remove/suspend teardown calls exit through the shared component path.

State and persistence behavior: state is in the `hdac_bus` audio component and hardware clock configuration; no persistent data is owned by this header.

Dependencies and integration points: includes `hda_component.h` and therefore DRM audio component/HDA core declarations. It is used by Intel HDA controller paths tied to i915 display audio.

Risks and edge cases: systems without i915 support must gracefully fall back; failed component init can disable HDMI/DP audio functionality; BCLK setup timing must match controller power state.

Test signals: compile both config paths, Intel HDMI/DP audio probe with i915 present and absent, runtime PM cycles, and stream startup after display power changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_i915.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_register.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_register.h

Source read summary: 368 lines, HD-audio controller register and bitfield map.

Purpose: centralizes Intel/HD-audio controller MMIO offsets, stream descriptor fields, CORB/RIRB constants, interrupt masks, buffer limits, and enhanced capability register layouts for standard and extended HDA links.

Important APIs, types, and functions: defines global registers such as `AZX_REG_GCAP`, `GCTL`, `INTCTL`, `CORB*`, `RIRB*`, immediate command/response, DMA position buffers, stream descriptor registers `AZX_REG_SD_*`, and stream control/status bits. It also defines hardware limits (`AZX_MAX_BDL_ENTRIES`, `AZX_MAX_BUF_SIZE`, CORB/RIRB entries), interrupt masks, SPIB/GTS/PP/ML capability IDs and offsets, multi-link bits such as `AZX_ML_LCTL_SPA/CPA`, synchronization fields, processing-pipe controls, and vendor-specific Intel offsets.

Control flow: controller code uses these constants to reset the controller, allocate/program CORB/RIRB and BDLs, start/stop stream DMA, service interrupts, parse extended capabilities, set stream sync and link power, and access multi-link HDA/SoundWire style registers.

State and persistence behavior: no software state is stored here; constants describe volatile MMIO state. Values written through these registers control DMA engine state, interrupt enablement, stream tags, FIFO/position tracking, and link power until reset or suspend.

Dependencies and integration points: uses generic bit helpers (`BIT`, `GENMASK`) and `HDA_MAX_CODECS` from HDA core users. It is consumed by `hdaudio.h` register-access macros and HDA controller implementations.

Risks and edge cases: incorrect offsets or masks can corrupt DMA, lose interrupts, or hang controller reset. Enhanced capability offsets differ by platform, and 32/64-bit address split registers require ordering discipline.

Test signals: controller reset and stream DMA tests on multiple Intel generations, interrupt mask validation, CORB/RIRB command tests, SPIB/position-buffer accuracy, multi-link capability parsing, and suspend/resume restoring registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_register.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_regmap.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_regmap.h

Source read summary: 225 lines, regmap encoding helpers for HD-audio verbs and amplifier controls.

Purpose: adapts HDA verb transactions to Linux regmap so codec drivers can cache, update, and sync selected verb/register state, including vendor verbs and amp gain/mute controls.

Important APIs, types, and functions: lifecycle and raw calls are `snd_hdac_regmap_init()`, `exit()`, `add_vendor_verb()`, `read_raw()`, `read_raw_uncached()`, `write_raw()`, `update_raw()`, `update_raw_once()`, and `sync()`. Encoding macros include `snd_hdac_regmap_encode_verb()`, `snd_hdac_regmap_encode_amp()`, and stereo variants. Inline helpers implement node/verb read/write/update and amp get/update for mono and stereo using `AC_AMP_FAKE_MUTE`, direction, channel, and index fields.

Control flow: codec setup initializes regmap, drivers use encoded verb helpers for cached writes or updates, raw uncached reads query hardware, and resume/sync pushes cached state back to the codec. Amp helpers split left/right channels when stereo control is requested.

State and persistence behavior: cache state is in `hdac_device->regmap`, protected by `regmap_lock`, with vendor verb definitions in `vendor_verbs`. It persists only across runtime operations within the device lifetime and is replayed after power transitions.

Dependencies and integration points: depends on `hdaudio.h`, HDA verb constants, regmap, and ALSA codec code. It integrates HD-audio widgets with generic kernel regmap caching and control update semantics.

Risks and edge cases: register encoding must avoid collisions between verbs, NIDs, amps, and vendor ranges; lazy cache mode can defer hardware writes while power is off; stereo helpers must preserve channel-specific bits.

Test signals: cache write/read/update-once behavior, resume sync after runtime suspend, amp mute/gain control updates, vendor verb registration, uncached reads, and collision tests for encoded register IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_verbs.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_verbs.h

Source read summary: 568 lines, HD-audio verb, parameter, capability, pin, power, and stream-format constants.

Purpose: provides the protocol vocabulary for communicating with HDA codecs: node IDs, function groups, verbs, parameter IDs, widget capability fields, pin defaults, pin controls, amp fields, digital converters, power states, unsolicited responses, and PCM format/rate bits.

Important APIs, types, and functions: constants include `AC_VERB_*` get/set commands, `AC_PAR_*` parameters, `AC_WCAP_*` widget capabilities, connection-list and amp masks, `AC_PINCAP_*`, `AC_PINCTL_*`, EAPD bits, digital converter bits, power-state fields, GPIO verbs, stream/channel fields, default pin config extraction macros, and supported rate/format bit definitions. The header is almost entirely macros/enums and intentionally defines no runtime functions.

Control flow: HDA core and codec parsers compose verbs from this header, send them through bus command paths, parse responses using masks/shifts, choose PCM formats/rates, configure pins/amps/power, and decode unsolicited events.

State and persistence behavior: no software state is owned; the macros describe codec hardware register state and response encodings. Drivers cache selected values in codec structs or regmap for restore.

Dependencies and integration points: consumed by `hdaudio.h`, `hda_codec.h`, `hda_regmap.h`, HDMI codecs, and vendor codec parsers. It mirrors the Intel HD Audio specification and is ABI-adjacent for hwdep verb tools.

Risks and edge cases: bitfield drift breaks every codec parser; pin default decoding is especially sensitive to shift/mask accuracy; unsupported vendor quirks may overload standard fields.

Test signals: codec enumeration on varied vendors, parser pin/amp/power tests, raw verb hwdep validation, supported PCM query tests, HDMI pin/ELD flows, and compile checks for macro users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdaudio.h -->
# sources/distributed-fs/ceph-client/include/sound/hdaudio.h

Source read summary: 765 lines, generic HD-audio core bus/device/stream interface.

Purpose: defines the reusable HD-audio core below legacy and ASoC HDA drivers: codec devices, bus command transport, CORB/RIRB bookkeeping, controller MMIO helpers, stream DMA descriptors, runtime PM helpers, widget arrays, DSP loader hooks, and PCI controller matching helpers.

Important APIs, types, and functions: `hda_nid_t`, `struct snd_array`, `struct hdac_device`, `struct hdac_driver`, `struct hdac_bus_ops`, `struct hdac_ext_bus_ops`, `struct hdac_rb`, `struct hdac_bus`, and `struct hdac_stream` are central. APIs cover device init/register, chip names/modalias, widget refresh, verb reads/writes, parameter overrides, connection parsing, PCM format generation, power up/down, driver matching, bus init/exit, command I/O, chip reset, stream IRQ handling, stream page allocation, stream assign/release/setup/start/stop/reset/sync, SPIB/DRSM/DPIB/LPIB operations, DSP prepare/trigger/cleanup, widget capability helpers, `snd_array` helpers, and GPU/controller PCI predicates.

Control flow: controller probe initializes `hdac_bus`, parses capabilities, resets the link, initializes command DMA, discovers codecs into `codec_list`, and registers `hdac_device` instances. Stream users assign an idle `hdac_stream`, set up BDL/format/periods, start DMA, handle IRQ status through bus callbacks, and release on close. Codec code sends verbs through `hdac_bus_ops` or device `exec_verb`; PM helpers wrap runtime power transitions.

State and persistence behavior: bus state includes MMIO base, IRQ, capability pointers, codec address table, unsolicited event ring/work, codec power mask, CORB/RIRB buffers and pending responses, stream list, DMA buffers, feature flags, locks, DRM display-power state, link list, and address offset. Stream state tracks BDL/position buffers, substreams, format tags, running/prepared flags, timestamps, and optional DSP lock. All state is device-lifetime and hardware-restored after reset/suspend.

Dependencies and integration points: depends on Linux device/PCI/PM/io/timecounter, ALSA core/PCM/memalloc, HDA verbs/registers, and DRM i915 component declarations. It underpins legacy HDA, ASoC HDA, HDMI/DP audio, DSP loading, and controller-specific drivers.

Risks and edge cases: command DMA vs PIO fallback, RIRB response timeouts, unsolicited ring wrap, aligned-MMIO platform differences, duplicate fields visible in this snapshot, stream tag reuse, DMA buffer alignment, and runtime PM during verb access are high-risk areas.

Test signals: codec discovery, CORB/RIRB and immediate-command paths, stream playback/capture DMA, interrupt and polling modes, runtime PM, display power integration, DSP loader paths, aligned MMIO builds, and multi-controller PCI matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdaudio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdaudio_ext.h -->
# sources/distributed-fs/ceph-client/include/sound/hdaudio_ext.h

Source read summary: 149 lines, extended HD-audio bus/link/stream contracts for ASoC and multi-link platforms.

Purpose: extends generic HDA core with link objects, extended streams, DMA parameter helpers, and bus operations used by Intel SST/SOF/ASoC HDA-style controllers.

Important APIs, types, and functions: `struct hdac_ext_link` tracks per-link index, capability address, codec mask, ML address, refcount, lock, and list nodes. `struct hdac_ext_stream` wraps `hdac_stream` with decoupled host/link DMA state, link stream tag/index/substream, and list nodes. APIs initialize/free extended bus and streams, assign/release streams, set up/clear host and link DMA, start/stop streams, sync start/stop, set stream IDs, enable links, get/set link power, configure stream decoupling, and open/close streams.

Control flow: extended controller probe initializes link lists, enumerates links from capability registers, allocates extended stream objects, then ASoC/SOF paths assign host/link streams separately and power links on demand before programming DMA.

State and persistence behavior: state is runtime kernel/controller state: link refcounts and power flags, assigned stream tags, decoupled host/link DMA flags, and stream lists. No disk persistence is involved.

Dependencies and integration points: includes HDA core and register definitions. It integrates with ASoC Intel DSP drivers, HDA multi-link controllers, SoundWire-adjacent HDA link management, and DMA parameter setup.

Risks and edge cases: host/link decoupling can leak stream tags or leave link DMA running; refcounted link power must balance under concurrent DAIs; capability parsing must handle missing or alternate ML registers.

Test signals: extended stream allocation, host/link setup and teardown, stream reset with decoupled mode, link power refcounting, multi-link enumeration, and SOF/SST playback/capture suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdaudio_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdmi-codec.h -->
# sources/distributed-fs/ceph-client/include/sound/hdmi-codec.h

Source read summary: 140 lines, ASoC HDMI codec platform API.

Purpose: defines the protocol between an ASoC CPU DAI/codec wrapper and an HDMI encoder/display driver for I2S or SPDIF audio.

Important APIs, types, and functions: `struct hdmi_codec_daifmt` describes DAI format, clock inversion/provider roles, and PCM/IEC958 bit format. `struct hdmi_codec_params` carries HDMI infoframe, IEC958 channel status, sample rate, sample width, and channel count. `hdmi_codec_plugged_cb` reports connector state. `struct hdmi_codec_ops` provides optional startup, mandatory `hw_params` or `prepare`, mandatory shutdown, optional mute, ELD fetch, DAI ID mapping, and plugged callback hook. `struct hdmi_codec_pdata` advertises I2S/SPDIF capabilities, capture/playback suppression, max I2S channels, and opaque encoder data.

Control flow: machine/encoder code registers a platform device with pdata; ASoC stream startup calls the encoder ops to configure infoframes and audio format, mutes/unmutes as needed, and shuts down at stream close. Hotplug can be forwarded through the callback.

State and persistence behavior: no state is stored in the header; runtime state lives in the codec driver, encoder private data, and connector/ELD cache.

Dependencies and integration points: includes OF graph, HDMI infoframes, ALSA IEC958/asound definitions, and ASoC. It connects SoC audio cards to DRM/display HDMI encoders.

Risks and edge cases: exactly one of prepare/hw_params must be supplied, ELD length and hotplug callback lifetime must be respected, and I2S/SPDIF capability flags must match DAI registrations.

Test signals: ASoC card probe, I2S and SPDIF stream startup/shutdown, IEC958 and infoframe contents, ELD read on hotplug, mute behavior, DAI endpoint ID mapping, and capture-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hdmi-codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hwdep.h -->
# sources/distributed-fs/ceph-client/include/sound/hwdep.h

Source read summary: 67 lines, generic ALSA hardware-dependent character device interface.

Purpose: declares `snd_hwdep`, its file operations, DSP firmware hooks, exclusive-open state, and constructor for exposing device-specific ALSA controls outside PCM/control APIs.

Important APIs, types, and functions: `struct snd_hwdep_ops` contains llseek/read/write/open/release/poll/ioctl/compat/mmap plus `dsp_status` and `dsp_load`. `struct snd_hwdep` stores card, list node, device number, id/name, interface type, optional OSS registration fields, ops, open waitqueue, private data/free, device pointer, open mutex, use count, loaded-DSP bitfield, and exclusive flag. `snd_hwdep_new()` allocates a hwdep instance for a card.

Control flow: a driver creates a hwdep device, fills ops/private fields, ALSA registers it with the card, and userspace opens it for device-specific ioctls, firmware loads, or mmap/read/write operations.

State and persistence behavior: state is per-card kernel object state and loaded-DSP flags. Firmware loaded through ops may persist in hardware until reset but is not persisted by ALSA.

Dependencies and integration points: depends on ALSA UAPI, poll, file/mm types, and card registration. Used by HDA, OPL3, SB CSP, and other special hardware interfaces.

Risks and edge cases: exclusive open and `used` count must be synchronized, compat ioctl must match native ABI, private data lifetime must survive open files, and DSP loaded bits must not desync from hardware.

Test signals: create/register/free, concurrent open/release, poll/read/write/ioctl/mmap operations, DSP status/load, OSS emulation builds, and module unload with open descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hwdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/i2c.h -->
# sources/distributed-fs/ceph-client/include/sound/i2c.h

Source read summary: 88 lines, ALSA legacy software/hardware I2C bus abstraction.

Purpose: provides bus, device, bit-bang, and mid-level operation structures for sound drivers that manage auxiliary I2C devices without using the generic Linux I2C core directly.

Important APIs, types, and functions: `struct snd_i2c_device` tracks list membership, bus, name, flags such as `SND_I2C_DEVICE_ADDRTEN`, address, private value/data/free. `struct snd_i2c_bit_ops` exposes start/stop/direction/setlines/getclock/getdata callbacks. `struct snd_i2c_ops` exposes send/read/probeaddr. `struct snd_i2c_bus` stores card, name, lock, master/slave bus list, devices, low-level ops, mid-level ops, and private data. Creation and transfer APIs are `snd_i2c_bus_create()`, `snd_i2c_device_create()`, `snd_i2c_device_free()`, `snd_i2c_sendbytes()`, `snd_i2c_readbytes()`, and `snd_i2c_probeaddr()`.

Control flow: a sound card creates a bus, optionally slaves it to a master sharing SCL/SCK, attaches devices, locks the master bus for transfers, and invokes send/read/probe through mid-level callbacks.

State and persistence behavior: state is in-memory card-lifetime bus/device lists and private driver data. External I2C device register changes persist only in hardware.

Dependencies and integration points: uses ALSA card structures, Linux list/mutex primitives, and codec/mixer drivers that need board-specific I2C access.

Risks and edge cases: master/slave locking must prevent shared-line contention, 10-bit addresses need correct flags, bit-bang callbacks can sleep or race if misused, and private_free order must match list removal.

Test signals: bus/device creation/free, shared master locking, byte send/read/probe, 7-bit and 10-bit addresses, concurrent transfers, and teardown with attached devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/info.h -->
# sources/distributed-fs/ceph-client/include/sound/info.h

Source read summary: 232 lines, ALSA procfs/info interface declarations.

Purpose: defines the proc/info entry model used by ALSA cards and modules to expose diagnostic text or binary data under `/proc/asound`.

Important APIs, types, and functions: `struct snd_info_buffer` describes print buffers, `struct snd_info_entry_text` and `struct snd_info_entry_ops` provide text or custom file operations, and `struct snd_info_entry` stores name, mode, size, content type, callbacks, parent/module/private data, proc entry, mutex, children, and list node. APIs cover global init/done, line/string parsing, module/card entry creation, freeing, card proc create/register/free/disconnect/id-change, entry registration, `snd_card_proc_new()`, `snd_info_set_text_ops()`, `snd_card_rw_proc_new()`, `snd_card_ro_proc_new()`, reserved-word checks, and optional OSS info.

Control flow: card setup creates proc entries, attaches read/write callbacks or custom ops, ALSA registers them with the card, and procfs invokes callbacks through seq/file wrappers. Disabled `CONFIG_SND_PROC_FS` builds compile to stubs.

State and persistence behavior: state is a hierarchy of in-memory `snd_info_entry` objects tied to modules/cards. Output is generated on read and not persisted; private_free handles driver-owned state on removal.

Dependencies and integration points: depends on procfs/seq_file/poll and ALSA core. It is used throughout ALSA for card, PCM, codec, OSS, and sequencer diagnostics.

Risks and edge cases: callback private data lifetime, module ownership, concurrent proc reads/writes, reserved path names, and config stubs returning success can hide missing diagnostics.

Test signals: proc entry creation/removal, read/write callbacks, card disconnect while files are open, `CONFIG_SND_PROC_FS=n` builds, OSS info paths, and parsing helpers with long lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/initval.h -->
# sources/distributed-fs/ceph-client/include/sound/initval.h

Source read summary: 90 lines, default module parameter and legacy resource discovery helpers.

Purpose: supplies standard ALSA defaults for card index, enable flags, ports, IRQs, DMA channels, DMA sizes, and optional legacy ISA/PnP resource probing helpers.

Important APIs, types, and functions: macros include `SNDRV_AUTO_PORT`, `SNDRV_AUTO_IRQ`, `SNDRV_AUTO_DMA`, `SNDRV_AUTO_DMA_SIZE`, single-card `SNDRV_DEFAULT_*1`, and array initializers for `SNDRV_CARDS`. Conditional helper functions are `snd_legacy_find_free_ioport()`, `snd_legacy_empty_irq_handler()`, `snd_legacy_find_free_irq()`, and `snd_legacy_find_free_dma()`.

Control flow: legacy drivers use these macros for module parameter defaults and, when enabled, scan candidate port/IRQ/DMA tables by temporarily requesting resources.

State and persistence behavior: no persistent state is stored. Probe helpers momentarily reserve and release resources and return the first available candidate.

Dependencies and integration points: depends on resource, interrupt, and DMA request APIs only when the corresponding `SNDRV_LEGACY_FIND_FREE_*` macros are defined. Used by ISA/legacy ALSA drivers.

Risks and edge cases: probing can race with real device claims, shared IRQ probing has side effects, defaults differ with `CONFIG_PNP`, and `SNDRV_AUTO_*` sentinel values must not be programmed into hardware.

Test signals: compile legacy drivers with each helper enabled, probe with occupied/free resources, PnP and non-PnP default enable arrays, and invalid resource table termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/initval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/intel-dsp-config.h -->
# sources/distributed-fs/ceph-client/include/sound/intel-dsp-config.h

Source read summary: 42 lines, Intel audio DSP driver selection interface.

Purpose: declares the policy API that selects between legacy HDA, SST, SOF, and AVS drivers for Intel PCI or ACPI audio devices.

Important APIs, types, and functions: enum values are `SND_INTEL_DSP_DRIVER_ANY`, `LEGACY`, `SST`, `SOF`, `AVS`, and `LAST`. Enabled builds expose `snd_intel_dsp_driver_probe()` for PCI and `snd_intel_acpi_dsp_driver_probe()` for ACPI HID devices. Disabled builds return `ANY`.

Control flow: Intel audio probe code asks this helper which driver family should bind before committing to a legacy or DSP stack.

State and persistence behavior: no state is stored in this header; implementation policy may inspect DMI, PCI IDs, ACPI, NHLT, and module parameters at runtime.

Dependencies and integration points: forward declares `pci_dev` and uses ACPI ID length via included environment. It gates HDA/SST/SOF/AVS driver integration.

Risks and edge cases: wrong selection can bind the wrong audio stack and break topology firmware loading or DMIC support; disabled config returns permissive `ANY`.

Test signals: platform matrix across Intel generations, ACPI HID matching, module override behavior, SOF/SST/AVS/legacy fallback, and compile without `CONFIG_SND_INTEL_DSP_CONFIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/intel-dsp-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/intel-nhlt.h -->
# sources/distributed-fs/ceph-client/include/sound/intel-nhlt.h

Source read summary: 199 lines, Intel NHLT ACPI audio table parser declarations.

Purpose: declares structures and helpers for discovering audio endpoints, formats, DMIC geometry, SSP link masks, and SoundWire link masks from Intel NHLT ACPI tables.

Important APIs, types, and functions: forward-facing helpers include `intel_nhlt_init()`, `intel_nhlt_free()`, `intel_nhlt_get_dmic_geo()`, `intel_nhlt_ssp_endpoint_mask()`, `intel_nhlt_ssp_mclk_mask()`, `intel_nhlt_ssp_link_mask()`, `intel_nhlt_has_endpoint_type()`, and `intel_nhlt_get_sdw_endpoint_mask()`, with disabled stubs returning neutral values. The header defines NHLT endpoint/link constants, vendor MIC array identifiers, and packed table descriptors such as endpoint descriptors, wave format/extensible format, format config, specific config, device-specific config, and vendor DMIC array config variants.

Control flow: Intel DSP/HDA/SOF probe loads the ACPI NHLT table, walks endpoint descriptors, filters by link/device type, extracts format/config blobs, derives DMIC count/geometry and SSP/SoundWire masks, then frees the table handle.

State and persistence behavior: state is a parsed table handle (`struct nhlt_acpi_table *`) owned by caller during probe. The ACPI firmware table is platform-provided and persistent firmware data, but parser state is temporary.

Dependencies and integration points: depends on ACPI table access, device logging, Intel DSP/SOF machine selection, DMIC topology, SSP/I2S links, and SoundWire link discovery.

Risks and edge cases: packed ACPI structures require exact layout, firmware may advertise malformed endpoint lengths, vendor DMIC geometry may not match topology files, and stubs can hide missing NHLT support.

Test signals: parse valid and malformed NHLT tables, DMIC 2/4-array detection, SSP endpoint/mclk/link masks, SoundWire endpoint masks, missing-table fallback, and compile with ACPI/NHLT disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/intel-nhlt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/jack.h -->
# sources/distributed-fs/ceph-client/include/sound/jack.h

Source read summary: 116 lines, ALSA jack abstraction API.

Purpose: defines shared reporting for audio/video/USB jack presence and headset button events through ALSA controls and optional input devices.

Important APIs, types, and functions: `enum snd_jack_types` is a bitmask for headphone, microphone, headset, line/video/AV, line-in, USB, and six button bits. `struct snd_jack` stores kcontrol list, card, ID, optional input device state/key map, cached hardware status, private data/free. APIs include `snd_jack_new()`, `snd_jack_add_new_kctl()`, `snd_jack_set_key()`, and `snd_jack_report()`, with config stubs when jack/input support is disabled.

Control flow: a codec or machine driver creates a jack, optionally adds extra kcontrols and key mappings, then reports status changes from GPIO, codec unsolicited events, polling, or USB detection.

State and persistence behavior: jack state is card-lifetime in-memory state plus `hw_status_cache`; userspace-visible switch/key events are emitted but not persisted.

Dependencies and integration points: depends on ALSA core and optional Linux input devices. Integrates ASoC, HDA, USB, and machine drivers with mixer controls and input event reporting.

Risks and edge cases: enum bits must stay synced with `sound/core/jack.c`, disabled stubs can hide missing reports, input key setup must precede registration, and cached status must handle phantom jacks.

Test signals: jack creation with/without initial kctl, headphone/mic/headset reports, button key events, input-disabled builds, phantom jack behavior, and concurrent report/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/jack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/madera-pdata.h -->
# sources/distributed-fs/ceph-client/include/sound/madera-pdata.h

Source read summary: 59 lines, Cirrus Logic Madera codec platform data.

Purpose: defines board/platform configuration fields for Madera-family codecs, including input modes, DMIC references, mono outputs, PDM speaker format, auxiliary power pins, and max clocked AIF channels.

Important APIs, types, and functions: constants define maximum inputs, muxed channels, outputs, AIFs, PDM speakers, and DSPs. `struct madera_codec_pdata` carries `max_channels_clocked`, `dmic_ref`, per-input `inmode`, `out_mono`, `pdm_fmt`, and `out_mono`/speaker related arrays referenced by the codec driver.

Control flow: board code or firmware translation fills the pdata before codec probe; the codec driver reads the arrays during initialization to program routing, bias, PDM, and clocking defaults.

State and persistence behavior: pdata is static board configuration copied or referenced at device probe. It does not store runtime state; hardware registers reflect the configuration until reset or reprogramming.

Dependencies and integration points: depends on Linux integer types and Madera codec driver definitions/datasheet values. Integrates platform data systems with ASoC codec setup.

Risks and edge cases: array dimensions must match maximum constants; wrong DMIC reference or input mode can damage capture routing; platform-data and device-tree/ACPI defaults must not conflict.

Test signals: probe each supported Madera variant with populated and default pdata, verify DMIC/input/output/PDM register programming, and check bounds for all max arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/madera-pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max9768.h -->
# sources/distributed-fs/ceph-client/include/sound/max9768.h

Source read summary: 20 lines, MAX9768 amplifier platform data.

Purpose: declares board data for the Maxim MAX9768 amplifier driver.

Important APIs, types, and functions: `struct max9768_pdata` contains `flags`, a signed `gain` value, and a `shdn_gpio` shutdown GPIO number.

Control flow: platform code provides pdata, the amplifier driver reads gain and shutdown GPIO configuration during probe, then uses the GPIO to enable/disable the amplifier.

State and persistence behavior: pdata is static configuration. Runtime gain/shutdown state lives in the codec/amplifier driver and hardware.

Dependencies and integration points: minimal Linux C header consumed by ASoC or codec amplifier drivers.

Risks and edge cases: invalid GPIO or out-of-range gain causes silent amplifier failure or wrong output level; board flags must match driver expectations.

Test signals: probe with valid/absent shutdown GPIO, gain programming, suspend/resume shutdown behavior, and pdata default handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max9768.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98088.h -->
# sources/distributed-fs/ceph-client/include/sound/max98088.h

Source read summary: 45 lines, MAX98088 codec platform data.

Purpose: supplies microphone, receiver, equalizer, and filter mode board configuration for the Maxim MAX98088 codec driver.

Important APIs, types, and functions: enums define microphone modes, receiver mode, EQ config names, and filter modes. `struct max98088_pdata` carries `eq_cfg`, `receiver_mode`, `digmic_left_mode`, `digmic_right_mode`, `exmode`, and `digmic_3_mode` style board choices.

Control flow: codec probe consumes pdata to select microphone inputs, receiver configuration, and optional EQ/filter settings before exposing ASoC controls/routes.

State and persistence behavior: configuration is static probe input; runtime mixer state is held by codec registers and ASoC controls.

Dependencies and integration points: consumed by MAX98088 ASoC codec driver and board files.

Risks and edge cases: enum values must match driver register programming; wrong digital mic mode can swap or disable capture; unsupported EQ names should fall back safely.

Test signals: codec probe with each mic/receiver mode, EQ/filter programming, suspend/resume restore, and default pdata path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98088.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98090.h -->
# sources/distributed-fs/ceph-client/include/sound/max98090.h

Source read summary: 24 lines, MAX98090 codec platform data.

Purpose: declares a compact board-data structure for MAX98090 analog/digital microphone and clocking setup.

Important APIs, types, and functions: `struct max98090_pdata` carries GPIO/wakeup and microphone/DMIC related configuration fields used by the codec driver at probe.

Control flow: board or firmware glue passes pdata to the codec driver; probe maps it into register defaults and DAPM route choices.

State and persistence behavior: no runtime state is stored here. Values are static configuration and hardware register state must be restored by the driver.

Dependencies and integration points: integrates platform-data based boards with the MAX98090 ASoC codec.

Risks and edge cases: absent pdata must produce safe defaults; incorrect mic/clock configuration can break capture or jack wake.

Test signals: probe with default and custom pdata, microphone path validation, jack/wakeup behavior, and suspend/resume register restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98090.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98095.h -->
# sources/distributed-fs/ceph-client/include/sound/max98095.h

Source read summary: 61 lines, MAX98095 codec platform data.

Purpose: defines board-provided EQ/BQ/DAI/microphone/receiver configuration for MAX98095-family codecs.

Important APIs, types, and functions: constants cover EQ and BQ configuration names/counts and DAI choices. `struct max98095_pdata` carries `eq_cfg`, `bq_cfg`, DAI configuration, receiver mode, digital mic modes, and jack/mic related board values.

Control flow: codec probe reads the pdata to choose filters, DAI routing/format assumptions, receiver path, and microphone inputs before registering controls and DAIs.

State and persistence behavior: pdata is static board state; active audio routing/filter state is in codec registers and ASoC runtime controls.

Dependencies and integration points: consumed by the MAX98095 ASoC codec driver and platform-board descriptions.

Risks and edge cases: configuration arrays/names must remain in sync with driver tables; invalid DAI/mic modes can misroute audio; missing pdata should not dereference null.

Test signals: probe filter presets, DAI selections, digital mic modes, receiver mode, no-pdata defaults, and suspend/resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/max98095.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/memalloc.h -->
# sources/distributed-fs/ceph-client/include/sound/memalloc.h

Source read summary: 120 lines, ALSA DMA buffer allocation abstraction.

Purpose: defines common DMA buffer descriptors, allocation types, synchronization helpers, mmap support, scatter-gather accessors, and devm allocation wrappers for ALSA PCM and control paths.

Important APIs, types, and functions: `struct snd_dma_device` stores DMA type, direction, sync requirement, and device. `struct snd_dma_buffer` stores device info, CPU area, DMA address, byte size, and allocator-private data. DMA type macros cover continuous, device, write-combined, IRAM, vmalloc, noncontiguous, noncoherent, and optional SG buffers. APIs include `snd_dma_alloc_dir_pages()`, `snd_dma_alloc_pages()`, fallback allocation, `snd_dma_free_pages()`, `snd_dma_buffer_mmap()`, `snd_dma_buffer_sync()`, `snd_sgbuf_get_addr/page/chunk_size()`, `snd_devm_alloc_dir_pages()`, and `snd_dma_noncontig_sg_table()`.

Control flow: PCM drivers request or preallocate buffers, set them into runtime state, map them to userspace if supported, sync for CPU/device access when needed, and free or devm-release at teardown.

State and persistence behavior: state is volatile DMA allocation metadata and memory. Audio samples persist only while buffers are allocated; allocator-private SG/noncontig data lives in `private_data`.

Dependencies and integration points: depends on Linux DMA mapping, pages, devices, vm_area, SG tables, and optional DMA/SG configs. It is used heavily by `pcm.h` and sound drivers.

Risks and edge cases: DMA direction and sync mode must match hardware, fallback allocations may reduce size, SG chunk math must not cross pages incorrectly, and mmap attributes must match cacheability.

Test signals: allocate/free each enabled DMA type, mmap and userspace access, noncoherent sync, SG address/page/chunk helpers, fallback paths under memory pressure, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/memalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/minors.h -->
# sources/distributed-fs/ceph-client/include/sound/minors.h

Source read summary: 97 lines, ALSA device minor numbering contract.

Purpose: defines static and dynamic minor-number layout for ALSA card devices, OSS emulation offsets, and helpers for deriving card/device numbers from minors.

Important APIs, types, and functions: macros include `SNDRV_MINOR_*` offsets for control, sequencer, timer, hwdep, rawmidi, PCM playback/capture, and OSS devices, plus `SNDRV_OS_MINORS`, `SNDRV_MINOR_DEVICES`, `SNDRV_MINOR_CARD()`, and `SNDRV_MINOR_DEVICE()`. Dynamic-minor builds change PCM device counts elsewhere.

Control flow: ALSA core uses these constants when registering character devices and resolving open minors back to card/device/interface instances.

State and persistence behavior: no runtime state is stored; minor allocation state lives in ALSA core. The numbering is ABI-visible and persistent across kernel/user expectations.

Dependencies and integration points: integrates ALSA core, UAPI device nodes, OSS emulation, PCM, rawmidi, hwdep, timer, and sequencer device registration.

Risks and edge cases: changing offsets breaks userspace device nodes; dynamic minors and OSS emulation must not collide; card/device extraction macros must match registration.

Test signals: device node creation for multiple cards, static vs dynamic minor builds, OSS emulation minors, open routing to correct ALSA device, and udev compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/minors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/mixer_oss.h -->
# sources/distributed-fs/ceph-client/include/sound/mixer_oss.h

Source read summary: 66 lines, ALSA OSS mixer emulation interface.

Purpose: declares the structures and registration helpers that map ALSA controls onto legacy OSS mixer device semantics.

Important APIs, types, and functions: `struct snd_mixer_oss_file` represents an open OSS mixer file, `struct snd_mixer_oss_slot` describes per-OSS-channel mapping/control state, and `struct snd_mixer_oss` stores card, device, slots, mask/stereo/record masks, and private state. APIs include OSS mixer register/disconnect functions, ioctl handling, and helpers for notifying control changes.

Control flow: when OSS emulation is enabled, ALSA card registration creates an OSS mixer facade; OSS ioctls are translated to ALSA control reads/writes through slots.

State and persistence behavior: state is per-card OSS mapping/cache state and open-file state. Mixer values persist in ALSA controls/hardware, not in this header.

Dependencies and integration points: depends on ALSA core/control and OSS emulation configs. It integrates `/dev/mixer` compatibility with native ALSA controls.

Risks and edge cases: channel masks and record-source semantics differ from ALSA controls; stereo/mono mapping can be lossy; disconnect must handle open OSS files.

Test signals: OSS mixer ioctls, volume and capture source mapping, stereo/mono controls, card disconnect with open files, and builds without OSS emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/mixer_oss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/mpu401.h -->
# sources/distributed-fs/ceph-client/include/sound/mpu401.h

Source read summary: 123 lines, MPU-401 UART/rawmidi interface declarations.

Purpose: provides constants, state, callbacks, and constructors for legacy MPU-401 MIDI UART devices.

Important APIs, types, and functions: macros define command/data/status offsets, status bits, reset/UART commands, hardware flags, and info flags. `struct snd_mpu401` stores port/resource, IRQ, hardware type, mode/timer/input/output flags, rawmidi/substream pointers, spinlock, timer, open masks, and private data/callbacks. Constructors include `snd_mpu401_uart_new()` and interrupt handler `snd_mpu401_uart_interrupt()`.

Control flow: a card driver creates the UART rawmidi device, opens input/output substreams, commands UART mode/reset, handles IRQs by reading/writing MIDI bytes, and closes or removes resources at teardown.

State and persistence behavior: state is per-device open/running/IRQ/timer/rawmidi state. MIDI bytes are transient; hardware UART mode persists until reset/power loss.

Dependencies and integration points: depends on ALSA rawmidi, timers, spinlocks, I/O ports, and legacy card drivers. It bridges MPU-401 compatible hardware to ALSA rawmidi.

Risks and edge cases: IRQ vs polling/timer modes, port resource ownership, open mask races, stuck status bits, and reset timing can drop MIDI data or hang close.

Test signals: UART creation, input/output rawmidi transfer, IRQ and timer fallback paths, reset command behavior, concurrent open/close, and hardware flag variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/mpu401.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h -->
# sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h

Source read summary: 39 lines, OMAP HDMI audio platform-data bridge.

Purpose: defines the pdata contract between OMAP display/HDMI code and its audio codec/DAI integration.

Important APIs, types, and functions: `struct omap_hdmi_audio_ops` exposes audio startup, shutdown, start, stop, and audio config callbacks. `struct omap_hdmi_audio_pdata` carries device pointer, opaque HDMI data, ops pointer, and DMA/audio configuration values for the platform driver.

Control flow: OMAP HDMI code provides pdata, the audio driver calls ops to configure and start HDMI audio streams, and shutdown/stop functions reverse the setup.

State and persistence behavior: pdata is static per-device glue; stream state lives in the OMAP HDMI/display and ASoC runtime drivers.

Dependencies and integration points: integrates TI OMAP DSS/HDMI blocks with ALSA/ASoC HDMI audio handling.

Risks and edge cases: callback lifetime and opaque data ownership must match device removal; config values must align with HDMI video/audio state.

Test signals: OMAP HDMI audio probe, stream start/stop, display hotplug/suspend interactions, invalid pdata handling, and callback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/opl3.h -->
# sources/distributed-fs/ceph-client/include/sound/opl3.h

Source read summary: 375 lines, Yamaha OPL2/OPL3/OPL4 FM synthesizer interface.

Purpose: declares FM synthesis register constants, instrument/patch formats, hardware voice state, OPL3 device state, hwdep file operations, sequencer integration, timer setup, and patch management.

Important APIs, types, and functions: register macros cover operator, envelope, wave, F-number, key-on/block, feedback/connection, stereo, rhythm, and OPL3 mode registers. `struct fm_operator`, `fm_instrument`, and `fm_patch` describe patch data. `struct snd_opl3_voice` tracks allocation state, note, key-on shadow, MIDI channel, and note-off timing. `struct snd_opl3` stores ports/resources, hardware type, command callback, timers, hwdep, card, mode/rhythm/max voices, optional sequencer clients/channel sets, patch hash table, voices, connection/drum shadows, and locks. APIs include create/init/timer/hwdep setup, open/ioctl/release/write, reset, patch load/find/clear.

Control flow: a legacy card creates the OPL3 object, initializes registers, exposes hwdep and optionally sequencer devices, then note/patch writes allocate voices and program operator/key registers. Timer interrupts and system timers handle note-offs and effects.

State and persistence behavior: state is per-card in-memory synth state plus shadow registers and loaded patch table. Hardware FM registers persist until reset; patches are not persisted across driver unload.

Dependencies and integration points: depends on ALSA hwdep, timer, sequencer, MIDI channel, resource/I/O, and legacy sound card drivers such as SB/OPL4.

Risks and edge cases: voice allocation races, patch hash lifetime, timer locking, OPL2 vs OPL3 register-bank differences, and 4-operator connection programming are fragile.

Test signals: OPL2/OPL3 create/reset, hwdep ioctl/write, patch load/find/clear, sequencer note on/off, timer interrupts, stereo/4-op modes, and builds without sequencer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/opl3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/opl4.h -->
# sources/distributed-fs/ceph-client/include/sound/opl4.h

Source read summary: 19 lines, OPL4 wavetable add-on constructor.

Purpose: declares creation of a Yamaha OPL4 component paired with an existing OPL3/FM device.

Important APIs, types, and functions: `struct snd_opl4` is forward-declared and `snd_opl4_create()` accepts a card, left/right ports, optional FM OPL3 pointer, hardware value, integrated flag, and output pointer.

Control flow: a legacy card driver creates OPL3 first when present, then calls `snd_opl4_create()` to register wavetable functionality on the adjacent ports.

State and persistence behavior: no state is defined here; OPL4 device state is owned by the implementation and hardware registers.

Dependencies and integration points: includes `opl3.h` and integrates OPL4 wavetable hardware with ALSA card setup.

Risks and edge cases: port pairing and integrated flags must match hardware; incorrect OPL3 association can break FM/wavetable coexistence.

Test signals: OPL4 creation with/without OPL3 pointer, port resource conflicts, integrated-card variants, and playback/sequencer registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/opl4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm-indirect.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm-indirect.h

Source read summary: 180 lines, helper layer for indirect PCM transfer engines.

Purpose: defines ring-position bookkeeping and helpers for drivers whose hardware DMA buffer differs from the ALSA runtime buffer, requiring staged copy between application and hardware areas.

Important APIs, types, and functions: `struct snd_pcm_indirect` stores hardware and application buffer bytes, hw/appl pointers, sw ready/room, transfer counter, min period, and optional byte-copy callback data. Inline helpers initialize, check boundaries, update positions, and copy playback/capture data. Public helpers include `snd_pcm_indirect_playback_transfer()`, `snd_pcm_indirect_capture_transfer()`, and pointer calculation utilities.

Control flow: a driver updates hardware position, calls the indirect transfer helper to move data between ALSA and device buffers, then reports elapsed periods based on bytes transferred and min period thresholds.

State and persistence behavior: state is runtime stream bookkeeping only. Buffer contents are transient audio data; no persistence is provided.

Dependencies and integration points: depends on ALSA PCM runtime/substream semantics and driver copy callbacks. Used by older ISA/PCI drivers with nonstandard DMA/FIFO engines.

Risks and edge cases: pointer wrap, byte/frame alignment, underrun/overrun detection, period elapsed timing, and copy callback error handling are high risk.

Test signals: playback/capture wraparound, small periods, noninterleaved formats if used, boundary alignment, underrun/overrun simulations, and pointer reporting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm-indirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm.h

Source read summary: 1595 lines, central ALSA PCM kernel API.

Purpose: defines the kernel-facing ALSA PCM model: hardware capability descriptors, driver callbacks, runtime/substream/card structures, state/trigger/rate/format constants, hardware-parameter constraints, timestamp packing, stream locking, availability helpers, transfer helpers, buffer allocation, mmap, channel maps, and 32/64-bit status ioctls.

Important APIs, types, and functions: key types include `struct snd_pcm_hardware`, `snd_pcm_ops`, `snd_pcm_file`, `snd_pcm_hw_rule`, `snd_pcm_hw_constraints`, `snd_ratnum`, `snd_ratden`, constraint lists/ranges, timestamp config/report, `snd_pcm_runtime`, `snd_pcm_group`, `snd_pcm_substream`, `snd_pcm_str`, `snd_pcm`, `snd_pcm_chmap_elem`, `snd_pcm_chmap`, and status structs. APIs/macros cover state setting/getting, stream locks, frame/byte/sample conversion, playback/capture availability/readiness, hw param mask/interval access, params accessors, interval refine/list/ranges/ratnum, constraint registration, format queries/silence, PCM creation/ops/sync, period elapsed, userspace/kernel transfer, rate masks, runtime DMA buffer setup, timestamp selection, preallocation/managed/fixed buffers, SG helpers, mmap, channel maps, and iov_iter I/O helpers.

Control flow: card drivers create PCM devices, set ops, advertise hardware capabilities and constraints, allocate buffers, then ALSA core drives open, hw_params, prepare, trigger, pointer, copy/page/mmap, ack, period elapsed, drain, stop, and close. Hardware/software params refine masks and intervals before runtime fields are committed; transfer helpers advance application and hardware pointers under stream locks.

State and persistence behavior: PCM state is rich but volatile: runtime status, hw/sw params, mmap status/control, waitqueues, async notifications, DMA buffer metadata, timestamp config, OSS emulation state, substream groups, refcounts, PM QoS, and channel maps. Audio sample data persists only while buffers remain allocated.

Dependencies and integration points: depends on ALSA UAPI/asound, memalloc, minors, poll/mm/bitops/PM QoS/refcount/uio, optional OSS emulation, and all PCM drivers. It is the main contract between ALSA core, hardware drivers, and userspace PCM ioctls.

Risks and edge cases: ABI layout changes, duplicate fields visible in this source snapshot, pointer boundary wrap, XRUN detection, stream lock ordering, mmap buffer lifetime, noncoherent DMA sync, 32-bit compat status, timestamp accuracy, and constraint refinement loops are critical.

Test signals: ALSA PCM selftests and userspace playback/capture, mmap and read/write transfers, all trigger commands, hw_params refinement matrices, nonstandard rates/formats, suspend/resume, XRUN recovery, 32-bit compat ioctls, channel map controls, and OSS emulation builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_drm_eld.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm_drm_eld.h

Source read summary: 98 lines, DRM ELD to ALSA PCM helper declarations.

Purpose: defines helpers and state for parsing HDMI/DP ELD data and exposing it through PCM/control logic.

Important APIs, types, and functions: `struct snd_pcm_chmap_elem` is referenced for channel maps. `struct snd_pcm_eld` style state stores ELD validity, monitor name, CEA speaker allocation, SAD count/data, and derived channel maps. Helpers update ELD, limit formats/rates/channels based on ELD, and create HDMI ELD controls for PCM devices.

Control flow: HDMI/DP audio code obtains ELD from DRM or codec pins, parses SAD/channel allocation, constrains PCM capabilities, and exposes monitor/ELD state to userspace controls.

State and persistence behavior: parsed ELD is cached per HDMI/PCM path and changes on hotplug or display mode changes. It mirrors sink firmware data and is not persisted by the kernel.

Dependencies and integration points: integrates ALSA PCM/channel-map controls with DRM connector ELD and HDMI audio codec paths.

Risks and edge cases: malformed ELD/SAD lengths, stale ELD after unplug, channel map mismatch, and overly restrictive constraints can break HDMI audio.

Test signals: hotplug ELD updates, invalid/short ELD parsing, SAD rate/format constraints, channel-map control contents, and monitor-name exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_drm_eld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_iec958.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm_iec958.h

Source read summary: 20 lines, IEC958 channel-status helper for PCM.

Purpose: declares a helper for filling AES/IEC958 status bytes from PCM runtime parameters.

Important APIs, types, and functions: `snd_pcm_create_iec958_consumer()` takes a runtime, output status buffer, length, and optional AES0 non-audio flag override.

Control flow: SPDIF/HDMI drivers call the helper after hw_params/runtime setup to generate consumer channel-status bits matching sample rate, format, and audio/non-audio mode.

State and persistence behavior: no state is stored. The generated status bytes are used by caller hardware/register programming.

Dependencies and integration points: depends on ALSA PCM runtime and IEC958/asound definitions through users. Integrates PCM params with digital audio transmitters.

Risks and edge cases: incorrect status bits can make sinks reject audio; buffer length must match expected IEC958 status size; compressed/non-audio formats need correct AES0 handling.

Test signals: status generation for common sample rates/formats, non-audio streams, short buffer handling, and HDMI/SPDIF playback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_iec958.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_oss.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm_oss.h

Source read summary: 75 lines, ALSA PCM OSS emulation data structures.

Purpose: defines per-runtime, per-substream, and per-stream state used to emulate legacy OSS PCM behavior on top of ALSA PCM.

Important APIs, types, and functions: structures track OSS buffer fragments, format/rate/channels, plugin/conversion state, mmap flags, trigger flags, bytes counters, period calculations, and OSS setup callbacks. These structs are embedded in `snd_pcm_runtime`, `snd_pcm_substream`, and `snd_pcm_str` when `CONFIG_SND_PCM_OSS` is enabled.

Control flow: OSS open/ioctl/read/write paths translate legacy parameters into ALSA hw/sw params, maintain fragment accounting, and use plugin/conversion helpers before forwarding to PCM transfers.

State and persistence behavior: state is open-stream emulation bookkeeping only. Audio data remains in PCM buffers and OSS parameters are not persisted after close.

Dependencies and integration points: used conditionally by `pcm.h` and ALSA OSS emulation implementation. It bridges `/dev/dsp` style applications to native PCM.

Risks and edge cases: fragment math, mmap compatibility, trigger semantics, format conversion, and full-duplex behavior differ from native ALSA and can regress old applications.

Test signals: OSS ioctl compatibility, fragment size/count behavior, mmap/read/write playback and capture, format/rate/channel conversion, trigger start/stop, and builds with OSS disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_oss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_params.h -->
# sources/distributed-fs/ceph-client/include/sound/pcm_params.h

Source read summary: 373 lines, ALSA PCM hw-parameter mask and interval helpers.

Purpose: provides inline operations for manipulating `snd_mask`, `snd_interval`, and typed accessors for `snd_pcm_hw_params` during PCM hardware-parameter refinement.

Important APIs, types, and functions: mask helpers include none/any/empty/min/max/set/reset/range/leave/intersect/equality/copy/test/single/refine/value. Interval helpers include any/none/checkempty/empty/single/value/min/max/test/copy/setinteger/equality. Params accessors expose access, format, subformat, channels, rate, period size/count, buffer size/bytes, width, physical width, and `snd_pcm_hw_params_bits()`.

Control flow: ALSA core and drivers initialize broad masks/intervals, apply constraints by intersecting/refining them, detect changes or emptiness, and finally read the selected single/min values into runtime hardware parameters.

State and persistence behavior: the helpers mutate caller-owned parameter structures only. No global state or persistence is involved.

Dependencies and integration points: included by PCM core and drivers using ALSA UAPI hw_param arrays. It is the low-level arithmetic engine for `snd_pcm_hw_refine()` and constraint callbacks.

Risks and edge cases: off-by-one bit indexing, empty interval detection with open endpoints, non-integer intervals, and assuming `.min` is final before refinement completes can produce invalid hw_params.

Test signals: unit-style tests for mask and interval operations, constraint refinement with empty/single ranges, all hw_param accessors, non-power-of-two steps, and unusual formats/subformats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pcm_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pt2258.h -->
# sources/distributed-fs/ceph-client/include/sound/pt2258.h

Source read summary: 23 lines, PT2258 volume-controller API.

Purpose: declares a small helper interface for the Princeton PT2258 six-channel electronic volume controller.

Important APIs, types, and functions: `struct snd_pt2258` is forward-declared. APIs include `snd_pt2258_reset()` and `snd_pt2258_build_controls()` to reset the chip and add ALSA mixer controls for a component.

Control flow: a card/codec driver creates or obtains a PT2258 instance, resets it during init, and builds volume controls tied to the ALSA card.

State and persistence behavior: no fields are defined here; runtime volume state lives in the implementation and chip registers.

Dependencies and integration points: integrates an external I2C-style volume chip with ALSA mixer/control registration.

Risks and edge cases: reset timing and control-value scaling must match hardware; missing reset may leave stale attenuation.

Test signals: reset command, control creation, volume/mute changes across all channels, and suspend/resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pt2258.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pxa2xx-lib.h -->
# sources/distributed-fs/ceph-client/include/sound/pxa2xx-lib.h

Source read summary: 59 lines, PXA2xx AC97 support declarations.

Purpose: declares shared AC97 controller helpers for PXA2xx-based platforms, including reset, suspend/resume, probe/remove, and optional SoC-specific hooks.

Important APIs, types, and functions: functions include `pxa2xx_ac97_read()`, `pxa2xx_ac97_write()`, `pxa2xx_ac97_reset()`, `pxa2xx_ac97_warm_reset()`, `pxa2xx_ac97_cold_reset()`, `pxa2xx_ac97_try_warm_reset()`, `pxa2xx_ac97_hw_suspend()`, `pxa2xx_ac97_hw_resume()`, `pxa2xx_ac97_hw_probe()`, and `pxa2xx_ac97_hw_remove()`. `struct pxa2xx_ac97_mach_ops` provides machine reset/warm/cold/suspend/resume operations.

Control flow: platform drivers install machine ops, probe hardware, perform cold/warm resets, then read/write AC97 codec registers through shared helpers. PM paths suspend/resume controller and codec link state.

State and persistence behavior: state lives in the AC97 controller implementation and machine ops pointer; codec registers persist only while powered or restored by driver.

Dependencies and integration points: bridges ARM PXA platform code, AC97 bus/codecs, and ALSA SoC/legacy drivers.

Risks and edge cases: reset sequencing is board-specific, read/write timeouts can hang probe, and suspend/resume hooks must preserve GPIO/clock state.

Test signals: cold/warm reset on target boards, codec register read/write, PM suspend/resume, missing machine ops fallback, and probe/remove resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/pxa2xx-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/q6usboffload.h -->
# sources/distributed-fs/ceph-client/include/sound/q6usboffload.h

Source read summary: 20 lines, Qualcomm QDSP6 USB offload parameters.

Purpose: defines the data passed for Qualcomm USB backend DAI link offload through QDSP6 audio paths.

Important APIs, types, and functions: `struct q6usb_offload` stores the USB backend device, allocated IOMMU domain, USB interrupter number, and stream ID (`sid`) for IOMMU transactions.

Control flow: Qualcomm audio machine/backend code fills this structure when configuring USB audio offload so DSP/audio code can address the USB device, interrupt, and IOMMU context.

State and persistence behavior: the structure is runtime configuration for an offload path; IOMMU domain lifetime is managed elsewhere and no state is persisted here.

Dependencies and integration points: integrates USB audio, Qualcomm QDSP6 ASoC backend, and IOMMU mapping.

Risks and edge cases: stale device/domain pointers, wrong interrupter number, or SID mismatch can break DMA isolation or offload interrupts.

Test signals: USB offload setup/teardown, IOMMU domain mapping, interrupter routing, multiple USB stream IDs, and disconnect during offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/q6usboffload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rawmidi.h -->
# sources/distributed-fs/ceph-client/include/sound/rawmidi.h

Source read summary: 203 lines, ALSA raw MIDI kernel interface.

Purpose: declares rawmidi devices, substreams, runtime buffers, file state, callbacks, creation, data transfer, kernel-open, params, drain/drop, and device tie helpers.

Important APIs, types, and functions: `struct snd_rawmidi_ops` defines open/close/trigger/drain, `struct snd_rawmidi_global_ops` handles device-level open/close/dev_register/dev_disconnect, `struct snd_rawmidi_runtime` stores buffer, size, avail/used/appl/hw pointers, xruns, locks, waitqueue, event flag, and private data. `struct snd_rawmidi_substream`, `snd_rawmidi_file`, `snd_rawmidi_str`, and `snd_rawmidi` define device topology and state. APIs include `snd_rawmidi_new()`, `set_ops()`, `init()`, `free()`, receive/transmit helpers, kernel open/release, params, drain/drop, and `snd_rawmidi_tie_devices()`.

Control flow: drivers create rawmidi devices, assign stream ops, open substreams from userspace or kernel clients, trigger input/output, move bytes through receive/transmit ring helpers, and drain/drop on close or ioctl.

State and persistence behavior: runtime ring buffers, pointer counters, avail/min/max sizes, active flags, and app/user PID state are volatile per open stream. MIDI data is not persisted.

Dependencies and integration points: depends on ALSA core/info, waitqueues, spinlocks, mutexes, and sequencer port info. Used by MPU-401, USB MIDI, virtual MIDI, and sequencer bridges.

Risks and edge cases: ring pointer wrap, xrun accounting, trigger/open races, drain waiting forever, kernel and userspace clients sharing streams, and tied-device lifetime.

Test signals: input/output byte transfer, buffer parameter changes, trigger start/stop, drain/drop, kernel open, sequencer integration, multiple subdevices, and disconnect with open streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rawmidi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt1015.h -->
# sources/distributed-fs/ceph-client/include/sound/rt1015.h

Source read summary: 15 lines, RT1015 platform data.

Purpose: supplies board-specific initialization delay for the Realtek RT1015 amplifier/codec driver.

Important APIs, types, and functions: `struct rt1015_platform_data` contains `power_up_delay_ms`.

Control flow: codec probe or power-up sequencing reads the delay and waits after enabling supplies/clocks before programming or unmuting the part.

State and persistence behavior: static board configuration only; runtime power state is in the codec driver/hardware.

Dependencies and integration points: consumed by the RT1015 ASoC codec driver.

Risks and edge cases: too short a delay can cause failed register access or pops; zero/default delay must match hardware tolerance.

Test signals: probe/power-up with configured delay, suspend/resume, and audio start after cold power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt1015.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt1318.h -->
# sources/distributed-fs/ceph-client/include/sound/rt1318.h

Source read summary: 16 lines, RT1318 platform data.

Purpose: provides initial left/right R0 calibration values for Realtek RT1318 smart amplifier setup.

Important APIs, types, and functions: `struct rt1318_platform_data` contains `init_r0_l` and `init_r0_r`.

Control flow: codec probe reads the calibration values and programs initial speaker impedance/resistance related registers before runtime calibration or playback.

State and persistence behavior: values are static board/calibration inputs; runtime calibration state is in the driver or hardware.

Dependencies and integration points: consumed by RT1318 ASoC codec/smart amp driver.

Risks and edge cases: swapped or invalid R0 values can affect protection/volume; missing pdata should fall back safely.

Test signals: probe with left/right calibration, register programming, default values, and speaker-protection behavior during playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt1318.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt286.h -->
# sources/distributed-fs/ceph-client/include/sound/rt286.h

Source read summary: 16 lines, RT286 platform data.

Purpose: declares board flags for Realtek RT286 combo jack and GPIO2 support.

Important APIs, types, and functions: `struct rt286_platform_data` contains booleans `cbj_en` and `gpio2_en`.

Control flow: codec probe enables combo-jack detection and GPIO2 functions based on pdata before registering jack/control paths.

State and persistence behavior: static board configuration only; jack/GPIO runtime state lives in codec registers and ALSA jack logic.

Dependencies and integration points: consumed by RT286 HDA/ASoC codec driver.

Risks and edge cases: wrong combo-jack flag breaks headset detection; GPIO2 conflicts with board wiring if enabled incorrectly.

Test signals: jack detection with cbj enabled/disabled, GPIO2 function tests, suspend/resume, and no-pdata defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt286.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt298.h -->
# sources/distributed-fs/ceph-client/include/sound/rt298.h

Source read summary: 17 lines, RT298 platform data.

Purpose: extends RT286-style board flags for Realtek RT298 with suspend power-off behavior.

Important APIs, types, and functions: `struct rt298_platform_data` contains `cbj_en`, `gpio2_en`, and `suspend_power_off`.

Control flow: codec probe configures combo jack/GPIO2; PM callbacks use `suspend_power_off` to decide whether codec power is removed during suspend and must be restored on resume.

State and persistence behavior: static configuration only; power-off means hardware register state may be lost and must be replayed by driver.

Dependencies and integration points: consumed by RT298 codec support and ALSA jack/PM flows.

Risks and edge cases: suspend power-off without full restore breaks audio/jack; GPIO2 and combo-jack flags must match board wiring.

Test signals: suspend/resume with power-off true/false, jack detection, GPIO2 behavior, and register restore after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt298.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5514.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5514.h

Source read summary: 19 lines, RT5514 platform data.

Purpose: supplies DMIC initialization delay and DSP calibration clock parameters for Realtek RT5514.

Important APIs, types, and functions: `struct rt5514_platform_data` contains `dmic_init_delay`, `dsp_calib_clk_name`, and `dsp_calib_clk_rate`.

Control flow: probe/power-up waits for DMIC readiness and configures or requests the calibration clock before DSP calibration/use.

State and persistence behavior: static board configuration; DSP calibration/runtime state is managed by the codec driver.

Dependencies and integration points: consumed by RT5514 codec/DSP driver and Linux clock framework through the named clock.

Risks and edge cases: missing clock name/rate or insufficient DMIC delay can break capture/calibration; clock lifetime must survive calibration.

Test signals: DMIC capture after init delay, DSP calibration clock request/rate programming, suspend/resume, and absent-clock fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5514.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5659.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5659.h

Source read summary: 47 lines, RT5659 platform data.

Purpose: describes Realtek RT5659 board wiring for differential inputs, LDO/reset GPIOs, DMIC data pins, and jack-detect source.

Important APIs, types, and functions: enums select DMIC1 data pin, DMIC2 data pin, and jack-detect source (`JD3` or HDA header). `struct rt5659_platform_data` contains `in1_diff`, `in3_diff`, `in4_diff`, `ldo1_en`, `reset`, `dmic1_data_pin`, `dmic2_data_pin`, and `jd_src`.

Control flow: codec probe requests GPIOs, resets/enables power, configures input modes, DMIC muxes, and jack detect according to pdata.

State and persistence behavior: pdata is static; GPIO and codec register state is runtime and restored by the driver.

Dependencies and integration points: consumed by RT5659 ASoC codec and board/machine descriptions.

Risks and edge cases: invalid GPIO numbers, wrong differential input flags, or jack source mismatch break audio routes or detection.

Test signals: probe GPIO handling, DMIC pin mux variants, differential input capture, jack detection, reset sequencing, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5659.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5660.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5660.h

Source read summary: 28 lines, RT5660 platform data.

Purpose: provides Realtek RT5660 board configuration for differential inputs, LDO2 use, suspend power-off, and DMIC1 data pin.

Important APIs, types, and functions: enum `rt5660_dmic1_data_pin` selects GPIO2 or IN1P. `struct rt5660_platform_data` contains `in1_diff`, `in3_diff`, `use_ldo2`, `poweroff_codec_in_suspend`, and `dmic1_data_pin`.

Control flow: codec probe configures input mode and DMIC mux; PM code uses the suspend power-off flag to decide restore requirements.

State and persistence behavior: static board data only; codec register and power state are runtime.

Dependencies and integration points: consumed by RT5660 ASoC codec driver.

Risks and edge cases: LDO and suspend policy must match board supplies; wrong DMIC pin disables capture; power-off requires full reinitialization.

Test signals: DMIC routing, differential inputs, LDO2 configuration, suspend/resume with poweroff, and defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5663.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5663.h

Source read summary: 22 lines, RT5663 platform data.

Purpose: supplies manual DC offset and impedance sensing calibration data for Realtek RT5663.

Important APIs, types, and functions: `struct rt5663_platform_data` contains manual left/right DC offsets for output and mic paths plus `impedance_sensing_num` and pointer to `impedance_sensing_table`.

Control flow: codec probe reads calibration fields, programs DC offset compensation, and uses the impedance table for jack/headset detection or tuning.

State and persistence behavior: table pointer and values are static configuration; active calibration state is hardware/driver state.

Dependencies and integration points: consumed by RT5663 codec driver and board firmware/platform data.

Risks and edge cases: dangling table pointer, count/table mismatch, or wrong offset values can degrade audio or headset detection.

Test signals: probe with table/count variants, DC offset register programming, impedance sensing, missing table fallback, and suspend/resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5663.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5665.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5665.h

Source read summary: 42 lines, RT5665 platform data.

Purpose: defines input, DMIC, jack-detect, and SAR headset type configuration for Realtek RT5665.

Important APIs, types, and functions: enums select DMIC1/DMIC2 data pins and jack-detect source. `struct rt5665_platform_data` contains differential flags for IN1-IN4, DMIC pin selections, `jd_src`, and `sar_hs_type`.

Control flow: codec probe programs input mode, DMIC muxes, jack detection, and SAR headset classification based on pdata.

State and persistence behavior: static board configuration; runtime jack/control state is in codec driver and ALSA jack layer.

Dependencies and integration points: consumed by RT5665 ASoC codec/machine drivers.

Risks and edge cases: pin mux mismatches break digital mics; SAR type mismatch affects headset button/type detection; differential flags must match PCB.

Test signals: all DMIC mux variants, jack/SAR detection, differential capture paths, no-pdata defaults, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5665.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5668.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5668.h

Source read summary: 34 lines, RT5668 platform data.

Purpose: describes DMIC data/clock pins and jack-detect source for Realtek RT5668.

Important APIs, types, and functions: enums select DMIC1 data pin, DMIC1 clock pin, and jack-detect source. `struct rt5668_platform_data` stores those selections.

Control flow: probe configures codec pin muxes for DMIC and jack detection before DAPM routes and controls are used.

State and persistence behavior: static configuration only; runtime pin/register state is managed by the codec driver.

Dependencies and integration points: consumed by RT5668 ASoC codec driver.

Risks and edge cases: data/clock pin mismatch prevents DMIC capture; wrong jack source disables detection.

Test signals: DMIC capture on each pin mapping, jack detect, suspend/resume restore, and default/null selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5668.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5682.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5682.h

Source read summary: 46 lines, RT5682 platform data.

Purpose: supplies DMIC pinning, jack-detect, button/DMIC timing, DMIC clock rate/drive, and DAI clock names for Realtek RT5682.

Important APIs, types, and functions: enums select DMIC1 data/clock pins, jack source, and DAI clock indexes. `struct rt5682_platform_data` stores pin selections, `btndet_delay`, `dmic_clk_rate`, `dmic_delay`, `dmic_clk_driving_high`, and `dai_clk_names`.

Control flow: codec probe requests named DAI clocks, configures DMIC mux/clock, jack detect, and button detection delays before runtime audio use.

State and persistence behavior: static board configuration; clock handles and codec registers are runtime state.

Dependencies and integration points: integrates RT5682 codec with clock framework, ASoC DAIs, DMIC capture, and jack/button detection.

Risks and edge cases: bad clock names, wrong DMIC clock rate, or insufficient delays can break capture or button detection; drive-high flag must match board electrical design.

Test signals: DAI clock lookup, DMIC capture at configured rate, button detection delay, jack source, suspend/resume, and null clock-name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5682.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5682s.h -->
# sources/distributed-fs/ceph-client/include/sound/rt5682s.h

Source read summary: 54 lines, RT5682S platform data.

Purpose: defines board configuration for RT5682I-VS/RT5682S including DMIC pins, jack source, DAI clocks, analog/digital mic delays, DAC reference LDO voltage, and DMIC drive strength.

Important APIs, types, and functions: enums select DMIC1 data/clock pins, jack source, DAI clock indexes, and LDO DAC reference voltage. `struct rt5682s_platform_data` stores DMIC/jack selections, clock rate, DMIC/AMIC delays, `ldo_dacref`, drive-high flag, and DAI clock names.

Control flow: probe configures supplies/reference voltage, DAI clocks, DMIC/AMIC timing, and jack routing from pdata.

State and persistence behavior: static board data only; runtime regulator/clock/register state is owned by the codec driver.

Dependencies and integration points: consumed by RT5682S ASoC codec, clock/regulator setup, DMIC and jack subsystems.

Risks and edge cases: invalid LDO enum can affect analog performance; clock/pin mismatch breaks capture; AMIC/DMIC delays need board-specific validation.

Test signals: probe all LDO settings, DAI clock names, DMIC/AMIC delay behavior, jack detect, suspend/resume, and defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/rt5682s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sb.h -->
# sources/distributed-fs/ceph-client/include/sound/sb.h

Source read summary: 363 lines, Sound Blaster legacy DSP/mixer/PCM interface.

Purpose: declares hardware types, DSP/mixer register constants, open/mode flags, core `snd_sb` state, DSP command helpers, mixer helpers, PCM/MIDI setup functions, and mixer-control construction macros for Sound Blaster compatible cards.

Important APIs, types, and functions: `enum sb_hw_type` classifies SB 1.x through ALS4000 variants. `struct snd_sb` stores card, ports/resources, IRQ/DMA, hardware version/type, mode/open/rate locks, mixer locks, rawmidi/PCM/OPL3 pointers, CSP pointer, and private fields. Macros define DSP I/O offsets, DSP commands, mixer device registers, IRQ/DMA setup bits, and mixer control encodings. APIs include DSP command/read/reset/create, mixer read/write/new/suspend/resume, SB8/SB16 PCM and MIDI setup/open/close/configure, PCM ops lookup, and mixer control add helpers.

Control flow: card probe resets the DSP, detects version, initializes mixer, configures IRQ/DMA, registers PCM/MIDI/OPL/CSP devices, and uses DSP commands to start/stop playback/capture DMA. IRQ handlers acknowledge 8/16-bit interrupts through inline helpers.

State and persistence behavior: per-card state tracks hardware resources, open modes, DMA/rate locks, mixer shadow behavior, and attached ALSA devices. Mixer/DSP registers persist only while hardware powered.

Dependencies and integration points: depends on ALSA core/control/PCM/rawmidi/timer/hwdep, OPL3, CSP, I/O port resources, and legacy ISA/PCI SB-compatible drivers.

Risks and edge cases: ISA DMA limits, IRQ/DMA setup mismatches, DSP reset timing, 8/16-bit mode conflicts, mixer register variants, and concurrent MIDI/PCM opens are fragile.

Test signals: DSP reset/version, SB8/SB16 playback/capture, MIDI UART, mixer controls, IRQ acknowledge, suspend/resume mixer restore, DMA channel variants, and ALS4000/DT019x register paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sb16_csp.h -->
# sources/distributed-fs/ceph-client/include/sound/sb16_csp.h

Source read summary: 76 lines, Sound Blaster 16 CSP/ASP control interface.

Purpose: declares the Creative Signal Processor state and operations used to load firmware codecs, control QSound, and integrate CSP through ALSA hwdep on SB16/AWE32 hardware.

Important APIs, types, and functions: program indexes cover mu-law, A-law, and ADPCM init/playback/capture. `struct snd_sb_csp_ops` provides use/unuse/autoload/start/stop/QSound transfer. `struct snd_sb_csp` stores SB chip pointer, exclusive use flag, codec metadata, accepted formats/channels/rates, mode/running state, ops, QSound locks/positions/controls, access mutex, and firmware program pointers. `snd_sb_csp_new()` creates the hwdep device.

Control flow: SB driver creates CSP hwdep, userspace or PCM paths load/autoload firmware, start CSP processing for selected sample width/channels, optionally transfer QSound position, then stop/unuse on close.

State and persistence behavior: firmware pointers and run/QSound state are in-memory; loaded CSP program may persist in hardware until reset but is not stored across unload.

Dependencies and integration points: includes SB core, hwdep, firmware loader, and UAPI CSP definitions. Integrates legacy DSP firmware processing with PCM/hwdep control.

Risks and edge cases: exclusive use locking, firmware lifetime, accepted-format validation, QSound concurrent updates, and hardware version compatibility.

Test signals: hwdep creation, firmware load/autoload for each program, start/stop for playback/capture, QSound controls, concurrent use rejection, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sb16_csp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca.h

Source read summary: 87 lines, MIPI SDCA function-discovery core declarations.

Purpose: defines SDCA device/function descriptors, device-wide SDCA data, quirks, and ACPI/SoundWire discovery/register helpers for SoundWire SDCA devices.

Important APIs, types, and functions: `SDCA_MAX_FUNCTION_COUNT` caps functions. `struct sdca_function_desc` stores firmware node, SDCA function device, name, type, and ACPI address. `struct sdca_device_data` stores interface revision, number of functions, descriptor array, and optional SWFT ACPI table. Quirks include RT712 VB and skipping function type patching. Enabled APIs look up functions, SWFT, interface revision, quirk matches, and register/unregister SDCA function devices; disabled stubs are no-ops/false/success.

Control flow: SoundWire slave probe discovers SDCA metadata from ACPI firmware, patches quirks, registers function child devices, and unregisters them on removal.

State and persistence behavior: discovered function data is per-slave runtime state derived from firmware tables/properties. Firmware data persists externally; kernel objects are device-lifetime.

Dependencies and integration points: depends on ACPI, firmware nodes, SoundWire slave devices, and optional `CONFIG_SND_SOC_SDCA`. It is the base for SDCA ASoC and FDL helpers.

Risks and edge cases: invalid function counts, firmware-node lifetime, SWFT parsing errors, and config stubs can hide missing SDCA support.

Test signals: ACPI SDCA function discovery, SWFT/interface revision parsing, quirk matching, child device registration/unregistration, max function bounds, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_asoc.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_asoc.h

Source read summary: 102 lines, SDCA to ASoC population helpers.

Purpose: declares helpers that translate SDCA function descriptors/data into ASoC DAPM widgets, routes, controls, DAIs, PCM constraints, ports, and hw_params behavior.

Important APIs, types, and functions: `SDCA_SINGLE_Q78_TLV` and `SDCA_DOUBLE_Q78_TLV` build mixer controls for signed 7.8 fixed-point volume registers using TLV callbacks. APIs count component objects, populate DAPM, controls, DAIs, and full component driver data, set/free PCM constraints, resolve SDCA ports, apply hw_params, and get/put Q7.8 volume controls.

Control flow: an SDCA function driver asks for object counts, allocates ASoC arrays, populates widgets/routes/controls/DAIs, registers the component, then uses constraint/port/hw_params helpers during PCM startup and parameter negotiation.

State and persistence behavior: this header owns no state. It fills caller-owned ASoC structures and manipulates SDCA regmap-backed runtime state through implementation functions.

Dependencies and integration points: forward-declares ASoC, regmap, PCM, and SDCA function types. It bridges generic SDCA descriptions to Linux ASoC component registration.

Risks and edge cases: Q7.8 sign/step handling, object count mismatch with allocation, lifetime of compound-literal mixer controls in macros, port resolution failures, and constraints not freed on error.

Test signals: component population for representative SDCA functions, TLV volume get/put, DAPM route/control counts, DAI hw_params, constraint set/free, and invalid function data handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_asoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_fdl.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_fdl.h

Source read summary: 105 lines, SDCA Function Download (FDL) state and helpers.

Purpose: declares state and control/status masks for SDCA function-download transactions plus helpers to allocate state, process interrupts, synchronize downloads, and reset functions.

Important APIs, types, and functions: `struct fdl_state` holds begin/done completions, timeout delayed work, mutex, attached interrupt, current FDL set, and file index. Macros define host/device FDL status combinations and masks: complete, more files, file available, file OK, more files OK, reset/abort/ack/needs-set bits. Enabled APIs are `sdca_fdl_alloc_state()`, `sdca_fdl_process()`, `sdca_fdl_sync()`, and `sdca_reset_function()`; disabled stubs return success.

Control flow: SDCA interrupt setup allocates FDL state, interrupt processing advances file/chunk transfer status, synchronization waits for begin/done completions and handles timeout work, and reset helper requests function reset through regmap.

State and persistence behavior: FDL state persists across interrupts during a download cycle only. Downloaded function files may affect device firmware/runtime state, but no persistent storage is defined here.

Dependencies and integration points: depends on completions, workqueues, mutexes, SDCA function data, interrupts, interrupt info, and regmap. It integrates SDCA firmware/function download with ASoC SDCA devices.

Risks and edge cases: timeout work racing IRQ handlers, incorrect mask interpretation, abort/reset sequencing, file index bounds, and disabled stubs falsely indicating download success.

Test signals: FDL allocation, interrupt-driven chunk/file progression, timeout and abort paths, multi-file sets, reset requests, sync completion ordering, and disabled-config compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_fdl.h -->
