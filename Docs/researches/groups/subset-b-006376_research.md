# subset-b-006376 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/hdmi_chmap.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/hdmi_chmap.c

Purpose: implements HDMI/DisplayPort channel allocation and ALSA channel-map controls for the HD-audio core. It bridges three representations: ELD speaker allocation bits, CEA Audio InfoFrame channel allocation indexes, and ALSA `SNDRV_CHMAP_*` positions.

Important APIs, types, and functions: `enum cea_speaker_placement`, `channel_allocations[]`, `hdmi_channel_mapping[][]`, `struct hdac_chmap_ops`, `snd_hdac_channel_allocation()`, `snd_hdac_setup_channel_mapping()`, `snd_hdac_get_active_channels()`, `snd_hdac_add_chmap_ctls()`, `snd_hdac_chmap_to_spk_mask()`, and `snd_hdac_spk_to_chmap()`. The file also supplies default operation callbacks for slot programming and converter channel count verbs.

Control flow: registration copies default callbacks into a caller-owned `struct hdac_chmap` and precomputes channel counts and speaker masks. Runtime allocation either derives a CEA CA from ELD speaker capabilities or validates a user-provided ALSA channel map. Setup then writes slot-to-channel assignments through `AC_VERB_SET_HDMI_CHAN_SLOT`; non-PCM streams use identity-like mapping, while PCM can use manual maps. Mixer TLV callbacks enumerate available maps based on the current sink speaker mask.

State and persistence: static CA tables are partly initialized at registration time; generated `hdmi_channel_mapping[ca]` entries persist globally. Per-pin/per-PCM maps live behind caller-provided ops. User changes are accepted only for open/setup/prepared PCM states and rejected while busy.

Dependencies and integration points: depends on HD-audio codec verbs, ALSA PCM channel-map controls, ELD speaker allocation from HDMI codec code, and caller-provided `hdac_chmap` hooks for per-pin state, validation, and PCM attachment.

Risks: CA selection is order-sensitive and explicitly notes possible wrong choices among multiple valid candidates. Manual maps with unknown positions are silently left unassigned until CA validation catches unsupported layouts. Global lazy initialization of mapping tables assumes stable static data and registration before use.

Test signals: validate stereo, 5.1, 7.1, non-PCM, and user-remapped playback with `amixer` channel-map controls; inspect HDMI InfoFrame CA and slot verbs with verbose HDA debugging; hotplug monitors with different ELD speaker masks; attempt map writes during running playback to confirm `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/hdmi_chmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/i915.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/i915.c

Purpose: connects HD-audio display audio with Intel graphics audio components (`i915` or `xe`) and programs Haswell/Broadwell display BCLK when the display power well or hotplug state changes.

Important APIs, types, and functions: `gpu_bind` module parameter, `snd_hdac_i915_set_bclk()`, `snd_hdac_i915_init()`, `connectivity_check()`, `i915_component_master_match()`, and `i915_gfx_present()`. Exported symbols are consumed by HDA controller drivers that need GPU display-audio services.

Control flow: initialization first decides whether a usable Intel display device exists and is allowed by `gpu_bind` and `nomodeset`. It scans PCI display devices, skips a denylist, and checks PCI bus topology. If present, `snd_hdac_acomp_init()` binds an audio component using the match callback. BCLK programming queries the graphics component for CDCLK frequency and writes HSW extended mode M/N registers.

State and persistence: module parameter `gpu_bind` affects all probes. Bound component state is stored on `bus->audio_component` and is cleaned up by the broader HD-audio component helpers. EM4/EM5 values are not persistent across display power-well loss and must be restored.

Dependencies and integration points: depends on PCI, DRM audio component interfaces, video `nomodeset`, HDA register macros, and the shared `snd_hdac_acomp_*` component binding layer. It recognizes both `i915` and `xe` driver names.

Risks: incorrect topology matching can bind to the wrong GPU on multi-GPU systems or miss discrete embedded HDA paths. New Intel display IDs may need denylist or topology updates. Missing graphics component ops causes `-EPROBE_DEFER`, so probe-order behavior is significant.

Test signals: boot systems with integrated and discrete Intel graphics, with and without `nomodeset`; verify display audio probe deferral and later binding; suspend/resume and hotplug on HSW/BDW while checking playback speed and EM4/EM5 restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/i915.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-dsp-config.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/intel-dsp-config.c

Purpose: central policy engine that chooses the Intel audio DSP driver family for PCI and ACPI devices: legacy HDA, SST, SOF, AVS, or any available implementation. The decision combines module override, PCI class, platform IDs, build-time Kconfig, DMI quirks, ACPI codec HIDs, NHLT, DMIC, and SoundWire discovery.

Important APIs, types, and functions: `dsp_driver` module parameter, `struct config_entry`, `config_table[]`, `acpi_config_table[]`, `snd_intel_dsp_driver_probe()`, `snd_intel_acpi_dsp_driver_probe()`, `snd_intel_dsp_find_config()`, `snd_intel_dsp_check_dmic()`, and `snd_intel_dsp_check_soundwire()`.

Control flow: PCI probing rejects non-Intel devices and old devices without PCI DSP selection. A valid positive module override wins. Otherwise PCI class identifies legacy-only or DSP-capable hardware. The ordered config table then applies first-match semantics, including DMI and codec-HID checks. Conditional flags require DMIC or SoundWire evidence before SOF/SST is returned. ACPI probing uses a smaller HID table and disallows forcing legacy for ACPI DSP devices.

State and persistence: there is no persistent runtime state beyond the read-only module parameter. The large static tables encode policy and depend heavily on compile-time `IS_ENABLED()` branches.

Dependencies and integration points: depends on ACPI, DMI, PCI IDs, SoundWire ACPI scanning, `intel-nhlt` helpers, and ASoC ACPI codec matching. It imports the `SND_INTEL_SOUNDWIRE_ACPI` namespace.

Risks: order-sensitive tables can shadow later quirks. Missing or malformed NHLT/SoundWire firmware can fall back to legacy even when digital mics or codecs require DSP. Module override can force unsupported selections. New platforms require table updates in both PCI IDs and Kconfig guards.

Test signals: matrix boots across SKL/KBL/APL/GLK/CNL/CML/ICL/TGL/ADL/RPL/MTL/LNL/PTL/NVL classes; compare selected driver with `dmesg`; test `dsp_driver=` overrides; verify ES83xx codec HID plus valid SSP endpoint; test DMIC-only and SoundWire-only firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-dsp-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-nhlt.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/intel-nhlt.c

Purpose: parses Intel ACPI NHLT tables for digital microphone geometry, endpoint presence, SSP/I2S masks, MCLK selection, endpoint format blobs, and SSP device type.

Important APIs, types, and functions: `intel_nhlt_init()`, `intel_nhlt_free()`, `intel_nhlt_get_dmic_geo()`, `intel_nhlt_has_endpoint_type()`, `intel_nhlt_ssp_endpoint_mask()`, `intel_nhlt_ssp_mclk_mask()`, `intel_nhlt_get_endpoint_blob()`, `intel_nhlt_ssp_device_type()`, plus helpers `nhlt_get_specific_cfg()` and `nhlt_check_ep_match()`.

Control flow: callers acquire the ACPI table, pass it into query helpers, then release it. Helpers linearly walk variable-length `struct nhlt_endpoint` records by advancing `epnt->length`. DMIC geometry combines array configuration with max channel count from format configs. Endpoint blob lookup filters by bus ID, link type, direction, and device type, then finds exact channel/rate/bit-depth match, with a DMIC-specific valid-bits exception for 32-bit samples.

State and persistence: no ownership is retained after `intel_nhlt_free()`. All state comes from firmware table contents and local iteration variables.

Dependencies and integration points: used by Intel DSP selection and ASoC machine/SOF setup to decide DMIC topology, SSP ports, and binary configuration blobs. Depends on ACPI NHLT structure definitions in `<acpi/nhlt.h>` and sound header constants.

Risks: most loops trust firmware-provided endpoint and config lengths, so malformed NHLT can cause bad traversal unless ACPI table validation already caught it. `intel_nhlt_ssp_mclk_mask()` requires exactly one MCLK across formats and returns `-EINVAL` otherwise. Device type lookup is strict and logs errors when firmware lacks matching SSP data.

Test signals: feed systems with no NHLT, DMIC-only, SSP/I2S, Bluetooth SSP, vendor-defined mic arrays, and mixed MCLK blobs; verify selected blobs for common rates and bit depths; fuzz or inspect firmware length fields in static analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-nhlt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-sdw-acpi.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/intel-sdw-acpi.c

Purpose: discovers Intel SoundWire controllers and enabled links from the ACPI namespace below an HDAS device.

Important APIs, types, and functions: module parameters `sdw_link_mask` and `sdw_ctrl_addr`, `sdw_intel_acpi_scan()`, `sdw_intel_acpi_cb()`, `sdw_intel_scan_controller()`, and `is_link_enabled()`. The exported function is namespaced as `SND_INTEL_SOUNDWIRE_ACPI`.

Control flow: `sdw_intel_acpi_scan()` walks ACPI device children to depth two, looking for `_ADR` values whose upper nibble marks SoundWire and whose address matches `sdw_ctrl_addr`. After finding the controller, `sdw_intel_scan_controller()` reads firmware properties: preferred `mipi-sdw-manager-list` or fallback `mipi-sdw-master-count`. It bounds link count, applies the module link mask, and checks each `mipi-sdw-link-%hhu-subproperties` child for a disable quirk.

State and persistence: result state is written into caller-provided `struct sdw_intel_acpi_info` as handle, count, and link mask. Module parameters globally override controller address and enabled links.

Dependencies and integration points: used by Intel DSP selection and SoundWire probe paths before hardware is powered. Depends on ACPI fwnode properties, SoundWire Intel constants, firmware child-node naming, and Linux property APIs.

Risks: firmware property absence prevents initialization. `count` and bit-list semantics differ when firmware supplies manager-list versus master-count, so sparse masks need coverage. Module overrides can hide links required by machine drivers. ACPI walk depth assumes SNDW is child or grandchild.

Test signals: test ACPI with manager-list, master-count, disabled link quirks, sparse link masks, no links, and too many links; exercise `sdw_link_mask=` and `sdw_ctrl_addr=`; confirm `info->link_mask` matches expected firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/intel-sdw-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/local.h -->
## sources/distributed-fs/ceph-client/sound/hda/core/local.h

Purpose: private HD-audio core header that shares internal helpers between core source files without exposing them as public sound API.

Important APIs, types, and functions: declares `hdac_dev_attr_groups`, widget sysfs lifecycle helpers, bus device add/remove/event/verb helpers, and `snd_hdac_exec_verb()`. It references `struct hdac_bus`, `struct hdac_device`, `hda_nid_t`, and `u32` via included users.

Control flow: no executable logic. The declarations connect sysfs, device, bus, and verb execution implementation files so they can call each other while keeping external headers narrower.

State and persistence: no state is defined in the header; it exposes functions that operate on caller-owned bus and codec state.

Dependencies and integration points: included by `regmap.c`, `sysfs.c`, and other HDA core implementation units. It acts as an internal boundary around sysfs attributes, widget tree maintenance, and verb dispatch.

Risks: because it is private, declarations must stay synchronized with implementations; accidental use outside core would couple external drivers to unstable internals. Missing includes in users can make type visibility fragile.

Test signals: compile HD-audio core after signature changes; check that only intended core files include it; verify exported public APIs remain in `<sound/hdaudio.h>` or related public headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/regmap.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/regmap.c

Purpose: maps HD-audio codec verbs into a regmap-backed pseudo-register interface with caching, power-management retries, and special handling for asymmetric verb encodings.

Important APIs, types, and functions: `snd_hdac_regmap_init()`, `snd_hdac_regmap_exit()`, `snd_hdac_regmap_add_vendor_verb()`, `snd_hdac_regmap_write_raw()`, `snd_hdac_regmap_read_raw()`, `snd_hdac_regmap_read_raw_uncached()`, `snd_hdac_regmap_update_raw()`, `snd_hdac_regmap_update_raw_once()`, `snd_hdac_regmap_sync()`, `hda_reg_read()`, `hda_reg_write()`, and `hda_regmap_cfg`.

Control flow: regmap callbacks classify readable/writeable/volatile pseudo registers, acquire codec power when needed, translate GET-style pseudo registers into SET verbs for writes, and execute HD-audio verbs. Raw helpers serialize on `codec->regmap_lock`, optionally use regcache, and retry `-EAGAIN` by power-cycling through PM.

State and persistence: per-codec state includes `codec->regmap`, `vendor_verbs`, regcache contents, `cache_coef`, `caps_overwriting`, and `lazy_cache`. Cached values survive until regmap exit and are synced on resume.

Dependencies and integration points: depends on Linux regmap, HD-audio verb execution, codec PM helpers, and `snd_array` for vendor verbs. Used by codec parsers and controls to avoid repeated direct verb handling.

Risks: pseudo-register encoding is subtle, especially stereo amp and coefficient access. Cache policy must mark volatile hardware state correctly; stale cache can misprogram resume. Lazy-cache behavior can hide write failures while powered down. `caps_overwriting` intentionally suppresses writes.

Test signals: test amp left/right writes, coefficient cache, vendor verbs, power-state reads, pin-sense volatile reads, suspend/resume regcache sync, and no-regmap fallback paths; enable dynamic debug for failed verb execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/stream.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/stream.c

Purpose: implements HD-audio stream lifecycle, DMA buffer descriptor programming, synchronization, timestamps, SPIB/DRSM helpers, and optional DSP firmware loading streams.

Important APIs, types, and functions: `snd_hdac_stream_init()`, `snd_hdac_stream_assign()`, `snd_hdac_stream_release()`, `snd_hdac_stream_reset()`, `snd_hdac_stream_setup()`, `snd_hdac_stream_set_params()`, `snd_hdac_stream_setup_periods()`, `snd_hdac_stream_start()`, `snd_hdac_stream_stop()`, `snd_hdac_stream_sync()`, `snd_hdac_stream_timecounter_init()`, SPIB/DRSM setters, and `snd_hdac_dsp_prepare()/trigger()/cleanup()` under `CONFIG_SND_HDA_DSP_LOADER`.

Control flow: streams move from unused to opened, prepared, running, stopped, cleaned, and released. Setup clears/reset registers, writes tag, buffer length, format, LVI, BDL addresses, position buffer, interrupts, FIFO size, and timing thresholds. BDL creation splits periods into hardware descriptors, including position-adjustment and 4K alignment quirks. Start/stop toggle interrupts and DMA start bits.

State and persistence: per-stream state includes opened/running/locked flags, assigned key, substream/compress stream, BDL DMA area, buffer and period sizes, format, stream tag, wallclock counters, SPIB/DRSM addresses, and cached thresholds. Bus-level locks protect assignment and DSP locks protect firmware loading.

Dependencies and integration points: used by HDA PCM and compressed paths, DSP loader, tracepoints, clocksource/timecounter, DMA helpers, and HDA controller register accessors.

Risks: descriptor count overflow, period adjustment greater than period size, register access-width quirks, and delayed RUN-bit clearing can break DMA. DSP loading must avoid races with normal PCM streams. Timestamp math assumes 24 MHz WALLCLK.

Test signals: run playback/capture across rates, channels, no-period-wakeup, SG buffers, 4K-aligned controllers, suspend/resume, synchronized multi-stream trigger, compressed streams, and DSP firmware loading; monitor tracepoints and underrun behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/sysfs.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/sysfs.c

Purpose: exposes HD-audio codec identity attributes and a widget-tree sysfs hierarchy under each codec device.

Important APIs, types, and functions: `hdac_dev_attr_groups`, `struct hdac_widget_tree`, `struct widget_attribute`, `hda_widget_sysfs_init()`, `hda_widget_sysfs_exit()`, `hda_widget_sysfs_reinit()`, `widget_tree_create()`, and per-attribute show callbacks for caps, pin config, PCM caps/formats, amps, power, GPIO, and connections.

Control flow: codec device attributes are installed through attribute groups. Widget init creates a `widgets` kobject, per-node kobjects named by NID, optional AFG kobject, and attribute groups. Show callbacks parse the NID from kobject names, recover the codec from the parent device, then read cached widget caps or issue HD-audio parameter/verb reads.

State and persistence: `codec->widgets` owns the root, AFG kobject, and node array. Reinit duplicates the tree metadata, prunes old NIDs, adds new ones, then swaps the tree pointer. Exit removes groups and releases kobjects.

Dependencies and integration points: depends on sysfs/kobject APIs, HDA codec parameter helpers, connection-list helpers, and internal `local.h` declarations. Device identity attributes are consumed by userspace diagnostics and modalias matching.

Risks: creation paths must unwind correctly after partial allocation; reinit currently ignores `add_widget_node()` return values while adding new nodes, which can hide failures. Attribute reads can trigger codec verbs and may depend on device power state handled by lower layers. NID parsing assumes stable two-hex-digit names.

Test signals: inspect `/sys/bus/hdaudio/.../widgets`, hot-reconfigure codecs with changed node ranges, run kmemleak/kobject reference checks, read all attributes during suspend/resume and after codec removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/trace.c -->
## sources/distributed-fs/ceph-client/sound/hda/core/trace.c

Purpose: instantiates HD-audio tracepoint definitions by defining `CREATE_TRACE_POINTS` and including `trace.h`.

Important APIs, types, and functions: no functions are defined directly. Its key symbol-level effect is generation of tracepoint objects for events declared in `trace.h`.

Control flow: compile-time only. One C file must include the trace header with `CREATE_TRACE_POINTS`; this file is that instantiation unit.

State and persistence: tracepoint static keys and event metadata are generated by the tracing subsystem at build/load time. Runtime trace buffers are owned by kernel tracing, not this file.

Dependencies and integration points: tightly coupled to `trace.h`, Linux tracepoint infrastructure, and stream/verb code that calls `trace_hda_*` and `trace_snd_hdac_stream_*` helpers.

Risks: duplicate `CREATE_TRACE_POINTS` inclusion would cause duplicate definitions; missing this file from the build would leave call sites unresolved. The include path settings in `trace.h` must stay compatible with this source location.

Test signals: build with tracing enabled, list events under `/sys/kernel/tracing/events/hda`, enable HDA command/response and stream start/stop events, and verify events appear during playback/probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/trace.h -->
## sources/distributed-fs/ceph-client/sound/hda/core/trace.h

Purpose: declares trace events for HD-audio command submission, codec responses, unsolicited events, and stream start/stop.

Important APIs, types, and functions: `TRACE_EVENT(hda_send_cmd)`, `TRACE_EVENT(hda_get_response)`, `TRACE_EVENT(hda_unsol_event)`, `DECLARE_EVENT_CLASS(hdac_stream)`, `DEFINE_EVENT(... snd_hdac_stream_start)`, and `DEFINE_EVENT(... snd_hdac_stream_stop)`.

Control flow: trace call sites pass bus and command/response/stream data into generated trace helpers. Fast-assign blocks snapshot device name, codec address, response words, and stream tag. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` allow `trace.c` to instantiate the events.

State and persistence: event definitions persist as tracing metadata; individual event records are transient in ftrace/perf buffers. No driver state is mutated.

Dependencies and integration points: included by HDA core code and the tracing generator. Depends on `linux/tracepoint.h`, `linux/device.h`, and `sound/hdaudio.h`.

Risks: event field choices are intentionally minimal; debugging requiring more stream context needs new fields with ABI awareness. The forward declaration names `struct hdac_codec`, while code mostly uses `struct hdac_device`; unused declarations should not drift into confusion.

Test signals: compile with `CONFIG_TRACING`; enable each event and confirm command values, codec addresses, unsolicited response tags, and stream tags match dynamic debug or hardware activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/core/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/Makefile -->
## sources/distributed-fs/ceph-client/sound/i2c/Makefile

Purpose: builds the ALSA-local I2C support modules and routes dependent sound-card Kconfig symbols to the required objects.

Important APIs, types, and functions: kbuild variables `snd-i2c-y`, `snd-cs8427-y`, `snd-tea6330t-y`, and `obj-$(CONFIG_...)` entries for `CONFIG_SND`, `CONFIG_SND_INTERWAVE_STB`, `CONFIG_SND_ICE1712`, and `CONFIG_SND_ICE1724`.

Control flow: when ALSA is enabled, the `other/` subdirectory is visited. InterWave STB pulls `snd-tea6330t.o` and `snd-i2c.o`; ICE1712 pulls `snd-cs8427.o` and `snd-i2c.o`; ICE1724 pulls only the generic `snd-i2c.o` from this directory, with additional codecs from `other/`.

State and persistence: no runtime state. It encodes module composition and link-time dependency state.

Dependencies and integration points: integrates the helper library with legacy PCI/ISA sound-card drivers that use ALSA's private bit-banged I2C abstraction rather than the generic Linux I2C subsystem.

Risks: missing object dependencies produce unresolved symbols for codec helper calls. Adding a new chip helper requires both object definition and appropriate `obj-*` dependency. Duplicate linkage can occur if multiple card configs pull the same helper into built-in objects, so kbuild behavior should be considered.

Test signals: build with `SND_INTERWAVE_STB`, `SND_ICE1712`, and `SND_ICE1724` as built-in and modules; inspect `modinfo` dependencies and unresolved symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/cs8427.c -->
## sources/distributed-fs/ceph-client/sound/i2c/cs8427.c

Purpose: controls the Cirrus Logic CS8427 IEC958/S/PDIF transceiver over ALSA I2C, including initialization, reset/PLL workaround, channel-status/user-data buffers, and PCM controls.

Important APIs, types, and functions: `struct cs8427`, `struct cs8427_stream`, `snd_cs8427_create()`, `snd_cs8427_init()`, `snd_cs8427_reg_write()`, `snd_cs8427_iec958_build()`, `snd_cs8427_iec958_active()`, `snd_cs8427_iec958_pcm()`, `snd_cs8427_reset()`, and control callbacks for input status, Q-subcode, masks, defaults, and PCM stream status.

Control flow: create allocates an ALSA I2C device, private cache, and calls init. Init verifies signature, writes grouped initialization registers, disables unused interrupts, initializes status buffers, then resets/run-starts the chip. PCM rate changes update IEC958 status bytes, notify controls, and reset the chip if the rate changed.

State and persistence: `regmap[0x14]` caches writable registers; playback and capture stream structures store substreams, hardware/default/PCM channel status, user data, and PCM control pointer. Rate and reset timeout persist in private data. Hardware status buffers are mirrored to avoid redundant writes.

Dependencies and integration points: uses `sound/i2c.h`, ALSA controls, PCM substreams, IEC958 status constants, bit reversal for CS/U data, and cards such as ICE1712.

Risks: the device has fixed addressing and register-window behavior; failed short I2C transfers map to `-EIO`. Reset waits on PLL unlock with jiffies timeout and can delay probe. Status/user-data writes assume correct buffer lengths.

Test signals: probe signature, S/PDIF playback at 32/44.1/48 kHz, PCM stream control activation, Q-subcode reads, input/error status reads, PLL lock after reset, and I2C fault injection for short transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/cs8427.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/i2c.c -->
## sources/distributed-fs/ceph-client/sound/i2c/i2c.c

Purpose: provides ALSA's legacy generic I2C abstraction and a default bit-banged implementation for sound-card helper chips.

Important APIs, types, and functions: `snd_i2c_bus_create()`, `snd_i2c_device_create()`, `snd_i2c_device_free()`, `snd_i2c_sendbytes()`, `snd_i2c_readbytes()`, `snd_i2c_probeaddr()`, `snd_i2c_bit_ops`, and the bit helpers for start, stop, send byte, read byte, and ACK.

Control flow: bus creation registers a `SNDRV_DEV_BUS` with the ALSA card and links optional slave buses under a master. Device creation links an addressable device under a bus. Send/read/probe dispatch through bus ops, defaulting to bit operations that toggle caller-provided line callbacks, send 7-bit address plus direction, and stop on completion or error.

State and persistence: bus state includes card, name, device list, slave bus list, master pointer, mutex, ops, hardware callbacks, and private free hook. Device state includes address, name, list linkage, bus pointer, flags, private data, and private free hook.

Dependencies and integration points: used by CS8427, TEA6330T, PT2258, and card-specific low-level line callbacks. It is separate from Linux's I2C core.

Risks: 10-bit addressing is unimplemented. Error paths sometimes call hardware stop instead of full bit stop after address/data failure. Correct behavior depends entirely on board-specific `setlines/getdata/direction` timing and locking by callers.

Test signals: probe valid/invalid addresses, exercise send/read with ACK/NACK, create/free buses with slave buses and devices, lockdep around `snd_i2c_lock()`, and board-level signal traces for start/stop timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/Makefile -->
## sources/distributed-fs/ceph-client/sound/i2c/other/Makefile

Purpose: builds additional ALSA I2C/serial helper codec modules used by legacy sound-card drivers.

Important APIs, types, and functions: kbuild variables `snd-ak4114-y`, `snd-ak4117-y`, `snd-ak4113-y`, `snd-ak4xxx-adda-y`, `snd-pt2258-y`, and `obj-$(CONFIG_SND_PDAUDIOCF/ICE1712/ICE1724)` dependency entries.

Control flow: PDAUDIOCF links AK4117; ICE1712 links AK4xxx AD/DA; ICE1724 links AK4114, AK4113, AK4xxx AD/DA, and PT2258 helpers. Each helper object exports symbols consumed by card drivers.

State and persistence: no runtime state; the Makefile persists build dependency mapping.

Dependencies and integration points: complements `sound/i2c/Makefile` and relies on Kconfig symbols from card drivers rather than standalone codec Kconfig entries.

Risks: helper objects are not selected independently, so card-driver dependencies must be kept exact. Moving helpers to a common library would require auditing symbol export and duplicate linkage behavior.

Test signals: allmodconfig and targeted builds for PDAUDIOCF, ICE1712, ICE1724; verify module dependency loading and absence of missing AK/PT symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4113.c -->
## sources/distributed-fs/ceph-client/sound/i2c/other/ak4113.c

Purpose: controls AK4113 S/PDIF receivers via caller-supplied read/write callbacks, exposing IEC958 status, errors, rate, input select, Q-subcode, and proc register dumps.

Important APIs, types, and functions: `snd_ak4113_create()`, `snd_ak4113_reg_write()`, `snd_ak4113_reinit()`, `snd_ak4113_build()`, `snd_ak4113_external_rate()`, `snd_ak4113_check_rate_and_errors()`, PM suspend/resume helpers, `ak4113_stats()`, and `ak4113_init_regs()`.

Control flow: create allocates and initializes the chip, copies programmable registers, resets/powers the device, snapshots receiver status, and registers an ALSA device. Build adds the IEC958 controls, proc entry, and starts delayed work. The polling work reads receiver status, counts errors, notifies controls on changed bits, invokes optional callbacks, and drains capture PCM if detected external rate differs from runtime rate.

State and persistence: `struct ak4113` holds cached writable registers, receiver status snapshots, error counters, controls, substream, delayed work, atomic work suppression counter, spinlock, and reinit mutex. Error counters are cleared on read.

Dependencies and integration points: card drivers provide hardware access callbacks and program bytes. ALSA controls and PCM runtime integrate with userspace and capture stream stopping. Procfs exposes register diagnostics.

Risks: polling and reinit concurrency is guarded by atomic counters and mutexes; misuse can leave work unscheduled. Control array indexes must match `AK4113_CONTROLS`. Firmware/hardware callbacks must be sleep-safe according to call context.

Test signals: capture from S/PDIF at each supported rate, induce parity/V/CRC errors, switch input, verify control notifications and error-counter clearing, suspend/resume reinit, and proc register readability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4113.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4114.c -->
## sources/distributed-fs/ceph-client/sound/i2c/other/ak4114.c

Purpose: controls AK4114 S/PDIF receivers/transmitters, including receive status monitoring and optional playback channel-status controls.

Important APIs, types, and functions: `snd_ak4114_create()`, `snd_ak4114_reg_write()`, `snd_ak4114_reinit()`, `snd_ak4114_build()`, `snd_ak4114_external_rate()`, `snd_ak4114_check_rate_and_errors()`, PM helpers, `ak4114_init_regs()`, `ak4114_stats()`, and `ak4114_notify()`.

Control flow: create copies six config registers and five TX channel-status bytes, initializes hardware through reset/power sequencing, snapshots receiver status, and registers the codec device. Build creates controls, skipping playback controls when no playback substream exists, adds a proc dump, and starts delayed polling. Polling reads status, updates error counters and snapshots, sends ALSA notifications, calls callbacks, and drains capture on rate mismatch.

State and persistence: cached state includes config `regmap`, `txcsb[]`, receiver status bytes, error counters, substreams, controls, delayed work, atomic work-processing counter, lock, and reinit mutex.

Dependencies and integration points: used by ICE1724-style drivers through callback IO. Integrates with ALSA PCM controls, procfs, PM, and optional playback S/PDIF status programming.

Risks: playback control mutation writes TX status without explicit locking in the put path. Control index assumptions in `ak4114_notify()` must remain aligned with `AK4114_CONTROLS`. Rate mismatch deliberately stops capture, so false rate decoding disrupts streams.

Test signals: capture/playback S/PDIF controls with and without playback substream, rate changes, error injection, delayed work cancel/restart during reinit and PM, proc register dump, and callback notification coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4117.c -->
## sources/distributed-fs/ceph-client/sound/i2c/other/ak4117.c

Purpose: controls AK4117 S/PDIF receivers via 4-wire callbacks, exposing capture IEC958 controls and timer-based status/error monitoring.

Important APIs, types, and functions: `snd_ak4117_create()`, `snd_ak4117_reg_write()`, `snd_ak4117_reinit()`, `snd_ak4117_build()`, `snd_ak4117_external_rate()`, `snd_ak4117_check_rate_and_errors()`, `snd_ak4117_timer()`, and the IEC958/error/input-select callbacks.

Control flow: create initializes locks, timer, cached programmable registers, performs reset/reinit, snapshots receiver state, and registers a codec device. Reinit deletes the timer, sets an init flag, reset/powers the chip, restores registers, clears init, and schedules immediate polling. The timer repeatedly checks errors and rate, notifies controls, invokes optional callbacks, and drains capture on rate mismatch.

State and persistence: `struct ak4117` stores cached registers, receiver snapshots, error counters, timer, init flag, substream, controls, callbacks, and spinlock. Unlike AK4113/4114, polling uses a timer instead of delayed work.

Dependencies and integration points: card drivers provide 4-wire read/write callbacks. ALSA controls expose capture status; PCM locking is used when stopping mismatched capture streams.

Risks: timer context constrains read/write callbacks; if callbacks sleep, this design is unsafe. The timer reschedules every jiffy, which can be noisy. Control index comments must stay aligned with header constants. Error counters clear on read.

Test signals: validate timer polling under lockdep/atomic-sleep debug, capture rate mismatch handling, input select writes, control notifications for every status bit, reinit timer shutdown/restart, and device free `timer_shutdown_sync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4xxx-adda.c -->
## sources/distributed-fs/ceph-client/sound/i2c/other/ak4xxx-adda.c

Purpose: generic helper for multiple AKM AD/DA converters, handling register cache writes, chip-specific initialization/reset, mixer control creation, TLV dB scales, capture selectors, deemphasis controls, and proc diagnostics.

Important APIs, types, and functions: `snd_akm4xxx_write()`, `snd_akm4xxx_reset()`, `snd_akm4xxx_init()`, `snd_akm4xxx_build_controls()`, chip reset helpers for AK4524/4528/4620, AK4529, AK4355/4358, AK4381, and mixer callbacks for volume, stereo volume, switches, capture source, and deemphasis.

Control flow: initialization selects chip defaults based on `ak->type`, sets chip count/name/register count, clears images and volumes, and writes initialization register/value sequences. Reset asserts or restores chip state per model. Control building walks DACs, ADCs, and deemphasis slots to synthesize `snd_kcontrol_new` structures with private bit-packed chip/register metadata and TLV scales.

State and persistence: state is caller-owned `struct snd_akm4xxx`: cached register images, separate logical volumes, chip/card metadata, DAC/ADC info arrays, and ops callbacks. Hardware writes update cache immediately.

Dependencies and integration points: used by ICE1712/ICE1724 family drivers with board-specific lock/write/unlock ops and channel naming. Exposes proc readout of cached registers.

Risks: many private-value bit fields and per-chip register mappings make off-by-one mistakes likely. Some controls set `access = 0` after previously configuring access flags. Volume conversion is nonlinear and chip-specific. Caller ops must lock correctly and tolerate initialization delays.

Test signals: initialize every supported chip type, compare cached register dumps to expected defaults, exercise DAC/ADC volumes including boundary values, mute switches, capture source enums, deemphasis controls, reset/restore, and custom channel naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/ak4xxx-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/pt2258.c -->
## sources/distributed-fs/ceph-client/sound/i2c/other/pt2258.c

Purpose: controls Princeton PT2258 six-channel volume controller over ALSA I2C, providing loopback volume and mute controls.

Important APIs, types, and functions: `snd_pt2258_reset()`, `snd_pt2258_build_controls()`, `pt2258_stereo_volume_info/get/put()`, `pt2258_switch_get/put()`, `pt2258_channel_code[]`, and `pt2258_db_scale`.

Control flow: reset sends reset, mute, and all-channel 0 dB commands, updating cached mute and volume state. Build creates three stereo volume controls for Mic, Line, and CD loopback and one mono loopback switch. Volume put translates ALSA 0..79 values to chip attenuation commands using tens and ones command nibbles for each physical channel.

State and persistence: the chip cannot be read back, so `struct snd_pt2258` caches `mute` and six `volume[]` attenuation values. I2C bus and device pointers are caller-owned and locked for each transfer.

Dependencies and integration points: used by ICE1724-era boards through ALSA private I2C. ALSA controls expose TLV scale from -79 dB to 0 dB.

Risks: cache and hardware can diverge after failed second-channel writes because the first channel may already have been updated. Mute state is updated before confirming I2C success. No readback exists to recover from bus errors except reset.

Test signals: reset sequencing, mute/unmute, boundary volumes 0 and 79 for all three stereo pairs, I2C short-transfer fault injection, and control cache consistency after failed writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/other/pt2258.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/tea6330t.c -->
## sources/distributed-fs/ceph-client/sound/i2c/tea6330t.c

Purpose: controls Philips TEA6330T sound fader/tone circuit over ALSA I2C, adding mixer controls for master volume/switch, bass, and optionally treble.

Important APIs, types, and functions: `struct tea6330t`, `snd_tea6330t_detect()`, `snd_tea6330t_update_mixer()`, `snd_tea6330t_restore_mixer()`, and control callbacks for master volume, master switch, bass, and treble.

Control flow: detect probes the fixed address. Update allocates a chip private structure, creates an ALSA I2C device, initializes fader/audio switch and tone defaults depending on equalizer mode, writes a contiguous register block, adds card component and controls, and appends to mixer name. Restore searches the bus device list for the TEA address and rewrites cached registers.

State and persistence: private state caches eight registers plus logical master left/right, bass, treble, max ranges, equalizer, and fader flags. The chip state is restored from cache after resume or card restore.

Dependencies and integration points: used by InterWave STB/UltraSound 32-Pro style cards. Integrates with ALSA mixer controls and the private `snd_i2c_bus` lock.

Risks: `strcat(card->mixername, ",TEA6330T")` assumes enough space. Volume put uses modulo rather than rejecting out-of-range values, matching old control style but surprising. Partial initialization failures must free the I2C device to avoid stale list entries.

Test signals: probe fixed address, equalizer enabled/disabled paths, mixer control ranges, mute switch, bass/treble writes, restore after suspend, and failure injection for initial block write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/i2c/tea6330t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/Kconfig -->
## sources/distributed-fs/ceph-client/sound/isa/Kconfig

Purpose: defines ALSA ISA sound-card configuration menu, helper-library symbols, card driver symbols, dependencies, and selected support libraries.

Important APIs, types, and functions: Kconfig symbols include helper tristates `SND_WSS_LIB`, `SND_SB_COMMON`, `SND_SB8_DSP`, `SND_SB16_DSP`, menu `SND_ISA`, and card symbols such as `SND_ADLIB`, `SND_AD1816A`, `SND_ALS100`, `SND_AZT*`, `SND_CMI*`, `SND_CS423*`, `SND_ES*`, `SND_GUS*`, `SND_INTERWAVE*`, `SND_SB*`, `SND_SSCAPE`, `SND_WAVEFRONT`, and `SND_MSND_*`.

Control flow: selecting `SND_ISA` gates all ISA cards behind ISA/compile-test, ISA DMA, and IO port support. Individual card options select required ALSA libraries such as PCM, TIMER, RAWMIDI, OPL3/OPL4, MPU401 UART, WSS, SB DSP, firmware loader, and sequencer components.

State and persistence: no runtime state; Kconfig choices persist in `.config` and shape the build graph and available modules.

Dependencies and integration points: integrates legacy ISA cards with ALSA core, PNP/ISAPNP, firmware loader, architecture constraints, and module names expected by users.

Risks: incorrect `select` usage can force invalid dependencies. Some drivers are architecture or firmware constrained. `SND_SB16_CSP` depends on `BROKEN || !PPC`, signaling known portability issues. Compile-test must still respect IO and DMA APIs.

Test signals: run `olddefconfig`, `allmodconfig`, `allyesconfig`, and targeted ISA configs on x86 and compile-test arches; verify selected helper libraries match object dependencies and module names in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/Makefile -->
## sources/distributed-fs/ceph-client/sound/isa/Makefile

Purpose: maps top-level ISA ALSA Kconfig symbols to module objects and descends into ISA card-family subdirectories.

Important APIs, types, and functions: object lists `snd-adlib-y`, `snd-als100-y`, `snd-azt2320-y`, `snd-cmi8328-y`, `snd-cmi8330-y`, `snd-es18xx-y`, `snd-opl3sa2-y`, `snd-sc6000-y`, `snd-sscape-y`, and `obj-$(CONFIG_...)` entries plus unconditional `obj-$(CONFIG_SND)` subdirectory traversal.

Control flow: selected simple ISA drivers build from one C object each. When ALSA is enabled, subdirectories for AD1816A, AD1848, CS423x, ES1688, Galaxy, GUS, MSND, OPTi9xx, SB, Wavefront, and WSS are visited, where their own Makefiles gate objects by card configs.

State and persistence: no runtime state; it encodes build composition.

Dependencies and integration points: follows Kconfig definitions in the same directory and lower-level Makefiles. It ties module names from help text to generated `snd-*` objects.

Risks: unconditional subdirectory traversal under `CONFIG_SND` relies on child Makefiles to avoid building disabled cards. Adding a top-level card requires updating both Kconfig and this Makefile. Line continuation must remain syntactically correct.

Test signals: targeted module builds for every top-level ISA symbol, `make M=sound/isa`, and checking that disabled child directories produce no unintended objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/Makefile -->
## sources/distributed-fs/ceph-client/sound/isa/ad1816a/Makefile

Purpose: builds the Analog Devices AD1816A ISA ALSA module from its probe/front-end and library implementation objects.

Important APIs, types, and functions: `snd-ad1816a-y := ad1816a.o ad1816a_lib.o` and `obj-$(CONFIG_SND_AD1816A) += snd-ad1816a.o`.

Control flow: when `CONFIG_SND_AD1816A` is enabled, kbuild links both `ad1816a.o` and `ad1816a_lib.o` into the `snd-ad1816a` module or built-in object.

State and persistence: no runtime state; the Makefile encodes module object composition.

Dependencies and integration points: paired with `SND_AD1816A` in `sound/isa/Kconfig`, whose dependencies select PNP, ISAPNP, OPL3, MPU401 UART, PCM, and TIMER support.

Risks: omitting either object would leave unresolved probe or library symbols. Since the parent Makefile always descends into `ad1816a/` under `CONFIG_SND`, this local `obj-*` guard is the sole build gate.

Test signals: build `CONFIG_SND_AD1816A=m` and `=y`, inspect resulting `snd-ad1816a` objects, and ensure disabling the symbol leaves the subdirectory with no built objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/Makefile -->
