# subset-b-006367 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/generic.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/generic.c

## Purpose
Implements the Linux HD-audio generic codec parser and runtime helper layer for codecs whose analog and digital routing can be derived from BIOS/default pin configuration. It turns `struct auto_pin_cfg` data into widget paths, mixer controls, PCM stream descriptors, jack callbacks, stream power management, EAPD/pin control programming, and generic probe/init/remove operations.

## Important APIs, Types, and Functions
The exported entry points are `snd_hda_gen_spec_init()`, `snd_hda_gen_add_kctl()`, `snd_hda_get_path_idx()`, `snd_hda_get_path_from_idx()`, `snd_hda_add_new_path()`, `snd_hda_activate_path()`, `snd_hda_gen_parse_auto_config()`, `snd_hda_gen_build_controls()`, `snd_hda_gen_build_pcms()`, `snd_hda_gen_init()`, `snd_hda_gen_remove()`, `snd_hda_gen_check_power_status()`, `snd_hda_gen_path_power_filter()`, `snd_hda_gen_stream_pm()`, `snd_hda_gen_fix_pin_power()`, `snd_hda_gen_update_outputs()`, the standard HP/line/mic jack callbacks, LED cdev helpers under `CONFIG_SND_HDA_GENERIC_LEDS`, and `snd_hda_gen_shutup_speakers()`. The module also registers a fallback `generic_driver` for QEMU/generic HDA IDs.

The central state object is `struct hda_gen_spec` from `generic.h`. This file mutates its dynamic arrays (`kctls`, `paths`, `loopback_list`), pin/ADC/DAC tables, control path indices, automute state bits, PCM records, power flags, and hook pointers. The most important local model is `struct nid_path`, a directional route through codec widgets with path NIDs, connection-selector indices, assigned amp controls, and activation/power flags.

## Control Flow
Generic codec probe allocates `hda_gen_spec`, initializes arrays and the PCM mutex, parses pin defaults with `snd_hda_parse_pin_defcfg()`, then calls `snd_hda_gen_parse_auto_config()`. The parser first applies user hints such as `auto_mute`, `multi_io`, `mixer_nid`, `power_down_unused`, `indep_hp`, `add_jack_modes`, and `hp_mic`. It collects all analog DACs, handles digital-only fallbacks, may promote headphone pins to primary output, then runs the output path evaluator.

Output parsing is a search-and-score process. `snd_hda_add_new_path()` recursively discovers routes from DACs to pins using `__parse_nid_path()`, respecting optional required or excluded anchor NIDs. `fill_and_eval_dacs()` tries hardwired routes, multi-I/O routes, shared DACs, preferred DACs, and alternate line-out/HP/speaker arrangements. `try_assign_dacs()` records the chosen route and accumulates a "badness" score from `hda_main_out_badness` or `hda_extra_out_badness`. The best scoring configuration is kept, volume/mute amp points are assigned with `assign_out_path_ctls()`, initial pin targets are cached, and aamix alternate paths can be added.

After output routing, the parser creates dynamic ALSA controls for playback volumes/switches, channel mode, independent HP, loopback mixing, shared HP/mic, input capture source, capture volume/switches, mic boost, jack mode enums, auto-mute mode, and digital SPDIF controls. Input parsing discovers analog ADCs, labels input pins, creates loopback mixer paths, creates capture paths from input pins to ADCs, detects dynamic ADC switching when no single ADC reaches all inputs, and creates auto-mic switching when a valid internal/external mic set exists.

Runtime init calls optional codec hooks, applies init verbs, restores pin targets, activates output/input/digital paths, replays aamix and loopback path state, clears unused unsolicited-event tags, synchronizes path power with jack state, runs automute/autoswitch callbacks, syncs the codec regmap, syncs virtual master mute hooks, and updates power status. PCM build creates up to three PCM devices: analog, digital, and alternate analog for independent HP or extra ADCs. PCM open/prepare/cleanup/close wrappers delegate to HDA multi-out helpers, set up or clean converter streams, maintain `active_streams`, support dynamic ADC retargeting, and invoke optional codec-specific PCM hooks.

## State and Persistence Behavior
Most state is in `codec->spec` and HDA codec register caches. Pin control targets are cached through `snd_hda_codec_set_pin_target()` and restored during init/resume; automute may temporarily write pin controls without changing the cached target. Path activation state is kept in `nid_path.active`, `pin_enabled`, `pin_fixed`, and `stream_enabled`; these drive amp muting and widget D0/D3 decisions. Dynamic kcontrol templates are stored only until `snd_hda_gen_build_controls()`, after which `free_kctls()` releases the temporary template names and array.

The file uses `spec->pcm_mutex` to serialize changes that conflict with active PCM streams, such as independent HP mode changes, and `codec->control_mutex` for bound mute/capture updates that temporarily rewrite `kcontrol->private_value`. LED class devices are registered into `spec->led_cdevs` and unregistered from `snd_hda_gen_spec_free()`. No state persists outside the kernel device lifetime except user-visible ALSA controls and hardware register/cache state restored across resume.

## Dependencies and Integration Points
This file depends heavily on the HDA codec core, auto parser, jack, beep, amplifier, SPDIF, virtual master, regmap, and ALSA control/PCM layers. It includes `hda_local.h`, `hda_auto_parser.h`, `hda_jack.h`, `hda_beep.h`, and `generic.h`. Codec-specific drivers can embed `hda_gen_spec`, set parser flags and hooks, call the exported parse/build/init helpers, override badness tables or preferred DACs, and provide LED or PCM hooks. The registered generic driver uses these helpers directly as a fallback codec implementation.

## Risks
The main risk is combinatorial routing: small changes to path discovery, DAC sharing, badness constants, or anchor handling can select different controls or break audio on unusual BIOS pin maps. Control ownership is subtle because path activation must not overwrite amp bits exposed as mixer controls. Automute can operate either by pin control or by amp mute bits, and mistakes can leave speakers live during headphone use or cause silent outputs. Dynamic ADC switching manipulates active converter streams and depends on `cur_adc_*` bookkeeping. Power-save path filtering depends on jack state and path activity, so stale path flags can power down widgets still needed by streams or loopback. Shared HP/mic and jack mode controls retask the same pin between input and output, which is sensitive to VREF handling and auto-mic suppression.

## Test Signals
Useful signals include boot/probe success on generic, Realtek-like, Conexant-like, QEMU, analog-only, digital-only, and mixed analog/digital codecs; `alsa-info` mixer names and channel maps matching expected pin layouts; headphone insertion muting speakers and optionally line-out; line-in/mic autoswitch selecting the correct input source; capture volume/switches affecting all intended paths; multi-I/O channel mode retasking pins without layout churn; suspend/resume restoring pin controls and streams; power-save-node tests showing inactive widgets in D3 and active/jack-present paths in D0; SPDIF controls appearing only when digital paths exist; and regression tests around `snd_hda_gen_shutup_speakers()` during suspend/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/generic.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/generic.h

## Purpose
Defines the public contract and state layout for the HD-audio generic parser implemented by `generic.c`. Codec drivers include this header to allocate/configure `struct hda_gen_spec`, describe preferred routing behavior, install hooks, and call the generic parse/build/init helpers.

## Important APIs, Types, and Functions
Key types are `struct hda_multi_io`, `struct nid_path`, `struct automic_entry`, `struct badness_table`, and `struct hda_gen_spec`. `struct nid_path` stores a route in DAC-to-pin order for output or pin-to-ADC order for input, including per-hop selector indices, multi-selector flags, assigned volume/mute/boost amp controls, and activation/power flags. `struct hda_gen_spec` is the large per-codec state object: it stores PCM stream templates and names, active stream bits and mutex, analog/digital routing data, ADC/DAC lists, auto-pin config, path index tables, automute state, parser behavior flags, loopback data, multi-I/O pins, preferred DAC pairs, virtual master/LED state, and hook callbacks.

The header declares generic lifecycle and parser functions: spec initialization/removal helpers, path lookup and creation, path activation, dynamic kcontrol creation, auto-config parsing, build controls, build PCMs, jack callbacks, output update, power management helpers, LED helpers, and speaker shutdown muting. It also exports the default output routing badness tables.

## Control Flow
Codec-specific drivers typically allocate `struct hda_gen_spec`, call `snd_hda_gen_spec_init()`, set parser flags or hooks, parse pin defaults, call `snd_hda_gen_parse_auto_config()`, then wire `snd_hda_gen_build_controls()`, `snd_hda_gen_build_pcms()`, and `snd_hda_gen_init()` into `hda_codec_ops`. During runtime, jack unsolicited callbacks can be routed to the standard HP, line-out, and mic autoswitch helpers declared here.

## State and Persistence Behavior
The header describes persistent per-device runtime state. Path arrays and kcontrol arrays are dynamic `snd_array` instances owned by the spec. Cached pin targets, current mux selections, current ADC stream metadata, automute booleans, mute bit masks, EAPD policy, channel count, independent HP enablement, and LED classdev pointers are all kept in the spec for the life of the codec. The state is not serialized to disk; it is reconstructed from codec defaults, hints, and driver flags on probe and restored to hardware during init/resume.

## Dependencies and Integration Points
It depends on Linux LED APIs and the HDA auto parser. It also references HDA core types, ALSA PCM/control types, `hda_multi_out`, `hda_input_mux`, `hda_vmaster_mute_hook`, and `hda_loopback_check` from included HDA headers. The integration contract is intentionally broad: vendor codec drivers can use the same parser while selectively overriding route preference, PCM stream templates, automute hooks, capture sync hooks, and LED behavior.

## Risks
Because `struct hda_gen_spec` is shared across many codec drivers, field ordering and semantics are an ABI-like internal kernel contract. Incorrect use of parser flags before parse time can silently change mixer topology. Path index arrays use one-based indices where zero means invalid, which is easy to misuse. Several arrays are bounded by auto-parser constants, so new hardware layouts with more pins, DACs, ADCs, or LEDs must respect those bounds or update them coherently.

## Test Signals
Compile coverage from multiple codec drivers is the first signal. Runtime signals include successful generic parser probe, correct allocation/freeing under probe failure and remove, expected mixer controls and PCMs for drivers using custom hooks, correct LED access flags when LED helpers are enabled, and no out-of-bounds path/mux references under unusual pin configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Kconfig

## Purpose
Defines the Kconfig menu for HD-audio HDMI and DisplayPort codec support. It lets the common HDMI support and vendor-specific HDMI codec drivers be built in, built as modules, or disabled, with individual controls visible to expert configurations.

## Important APIs, Types, and Functions
This is configuration metadata rather than C code. The top-level `SND_HDA_CODEC_HDMI` `menuconfig` gates all HDMI/DP codec choices. Sub-options include `SND_HDA_CODEC_HDMI_GENERIC`, `SND_HDA_CODEC_HDMI_SIMPLE`, `SND_HDA_CODEC_HDMI_INTEL`, `SND_HDA_INTEL_HDMI_SILENT_STREAM`, `SND_HDA_CODEC_HDMI_ATI`, `SND_HDA_CODEC_HDMI_NVIDIA`, `SND_HDA_CODEC_HDMI_NVIDIA_MCP`, and `SND_HDA_CODEC_HDMI_TEGRA`.

## Control Flow
When HDMI support is selected, the generic and vendor codec options default to `y`; under `CONFIG_EXPERT`, users can tune them individually. Intel, AMD/ATI, Nvidia, and Tegra options select the generic HDMI codec support where they extend the generic implementation. Legacy Nvidia MCP selects the simpler HDMI support. Intel silent stream is a bool that depends on Intel HDMI support and enables keep-alive/silent-stream behavior on capable hardware.

## State and Persistence Behavior
Kconfig choices persist in the kernel `.config` and drive compilation and module availability. They do not create runtime state directly, but their selected symbols decide which objects and feature code enter the build.

## Dependencies and Integration Points
`SND_HDA_CODEC_HDMI_GENERIC` selects `SND_DYNAMIC_MINORS` for DP-MST multi-stream minor allocation and `SND_PCM_ELD` for ELD parsing/support. Vendor options select generic or simple HDMI support and are consumed by the HDMI `Makefile` to build the corresponding modules. The options integrate with ALSA HDA codec registration and GPU audio component behavior once compiled.

## Risks
The top-level option text contains a typo, "DislayPort", but behavior is unaffected. Functional risk is mainly dependency drift: failing to select `SND_DYNAMIC_MINORS`, `SND_PCM_ELD`, or the right generic/simple base would produce missing symbols or incomplete DP-MST/ELD behavior. Defaults to `y` under the parent can increase build surface unless expert users disable drivers.

## Test Signals
Kconfig tests should verify valid `y`, `m`, and `n` combinations; dependency propagation for generic, Intel, AMD/ATI, Nvidia, Nvidia MCP, and Tegra; successful builds for modular and built-in configurations; and presence or absence of the expected `snd-hda-codec-*` modules matching the selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Makefile

## Purpose
Maps HDMI/DisplayPort HDA codec Kconfig symbols to the object files and modules that implement generic, simple, and vendor-specific HDMI audio support.

## Important APIs, Types, and Functions
The Makefile adds `-I$(src)/../../common` to subdirectory C flags. It defines composite objects: `snd-hda-codec-hdmi-y := hdmi.o eld.o`, `snd-hda-codec-simplehdmi-y := simplehdmi.o`, `snd-hda-codec-intelhdmi-y := intelhdmi.o`, `snd-hda-codec-atihdmi-y := atihdmi.o`, `snd-hda-codec-nvhdmi-y := nvhdmi.o`, `snd-hda-codec-nvhdmi-mcp-y := nvhdmi-mcp.o`, and `snd-hda-codec-tegrahdmi-y := tegrahdmi.o`. The `obj-$(CONFIG_...)` lines connect these composites to Kconfig symbols.

## Control Flow
Kbuild evaluates each `obj-$(CONFIG_*)` assignment and builds the relevant module or built-in object. Generic HDMI combines the main HDMI implementation with ELD helper code. Vendor-specific drivers compile as separate modules that import or call generic HDMI support depending on their C implementation and Kconfig selection.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is the kernel build graph and the final set of built-in objects or loadable modules.

## Dependencies and Integration Points
It integrates with the HDMI Kconfig file and kbuild's composite object convention. The include path gives HDMI codec code access to common HDA helpers. The generic object depends on both `hdmi.o` and `eld.o`, so ELD routines are packaged with generic HDMI support.

## Risks
Risks are build-graph mismatches: omitting `eld.o` from the generic object would break ELD symbols, associating an object with the wrong config would build unsupported drivers, and include-path changes could hide shared headers. Vendor modules also rely on Kconfig selecting the correct base support to avoid unresolved imports.

## Test Signals
Build all HDMI configs as built-in and module, inspect `modules.order` or linked objects for expected `snd-hda-codec-hdmi`, `simplehdmi`, `intelhdmi`, `atihdmi`, `nvhdmi`, `nvhdmi-mcp`, and `tegrahdmi` outputs, and run modpost to catch missing imports or namespace annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/atihdmi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/atihdmi.c

## Purpose
Implements the AMD/ATI HDMI and DisplayPort HD-audio codec driver. It layers AMD-specific verbs, ELD emulation, channel mapping, HBR control, ramp-rate setup, and GPU audio-component binding on top of the generic HDMI codec implementation.

## Important APIs, Types, and Functions
The driver defines AMD vendor verbs for channel allocation, downmix info, multichannel slot mapping, HBR control, ramp rate, and sink/ELD emulation. `get_eld_ati()` synthesizes a baseline ELD buffer from AMD-specific speaker allocation, sink info, audio descriptor, and latency verbs. `atihdmi_pin_get_eld()`, `atihdmi_pin_setup_infoframe()`, `atihdmi_pin_hbr_setup()`, and `atihdmi_setup_stream()` are installed into `hdmi_spec.ops`. Channel-map overrides include `atihdmi_pin_set_slot_channel()`, `atihdmi_pin_get_slot_channel()`, `atihdmi_paired_chmap_validate()`, `atihdmi_paired_chmap_cea_alloc_validate_get_type()`, and `atihdmi_paired_cea_alloc_to_tlv_chmap()`.

The module registers `atihdmi_codec_ops`, an HDA ID table for RS600/RS690/R6xx HDMI devices, and `atihdmi_driver` via `module_hda_codec_driver()`. It imports the `SND_HDA_CODEC_HDMI` namespace.

## Control Flow
Probe first calls `snd_hda_hdmi_generic_probe()` and then customizes the returned `struct hdmi_spec`: static PCM mapping is enabled, AMD-specific pin/stream ops are installed, and channel-map ops are overridden. Pre-rev3 AMD codecs use pairwise channel remapping with FC/LFE swap handling; rev3-or-later codecs support full per-channel remap and single-channel mode. Probe also expands converter capability fields because AMD converters do not advertise all rates, formats, channel counts, or bit depths, enables link-down-at-suspend, and binds to the DRM audio component with AMD pin-to-port mapping.

Init delegates to `snd_hda_hdmi_generic_init()`, clears downmix info on every pin, enables single-channel multichannel mode on full-remap hardware, and enables auto runtime PM. Stream setup writes an AMD ramp-rate verb on rev3+ hardware, disabling ramp for non-PCM formats, then calls generic HDMI stream setup. Runtime callbacks for ELD, infoframe channel allocation, HBR, and slot mapping issue AMD vendor verbs against the pin or converter NIDs.

## State and Persistence Behavior
Persistent device state lives in `codec->spec` as the generic `hdmi_spec` plus AMD-installed ops and modified converter capabilities. Hardware state includes pin downmix info, multichannel mode, slot-channel mapping, HBR enable state, channel allocation, and converter ramp rate. `get_eld_ati()` writes sink-info/audio-descriptor indices before reading associated data but stores the synthesized ELD only in the caller-provided buffer.

## Dependencies and Integration Points
The file depends on Linux module/init/slab/unaligned helpers, ALSA core/TLV/HDA APIs, `hda_local.h`, and `hdmi_local.h`. It integrates with generic HDMI helpers for probe/remove/init/build PCMs/build controls/unsolicited events/suspend/resume and with DRM audio-component callbacks for pin ELD notifications and master bind/unbind. The Kconfig option selects generic HDMI support and the Makefile builds this as `snd-hda-codec-atihdmi`.

## Risks
Pre-rev3 pairwise remapping is fragile: odd/even slots, silent companion channels, and FC/LFE swapping must agree between validation, TLV generation, set, and get paths. `get_eld_ati()` synthesizes standardized ELD from vendor registers, so incorrect SAD count, sink-name length truncation, alignment, or latency conversion can make user space see wrong sink capabilities. The driver assumes AMD pin NIDs map to ports as `pin / 2 - 1` and reverse as `port * 2 + 3`; new hardware layouts could violate that convention. Forcing converter capabilities may advertise functionality the hardware or sink path cannot actually use if assumptions become stale.

## Test Signals
Signals include successful probe/init on listed AMD IDs, valid `/proc/asound` or control ELD data for HDMI and DP sinks, correct PCM capability exposure up to 8 channels/24 bit/supported rates, working HBR passthrough for capable pins and rejection on incapable pins, channel-map validation for pre-rev3 pairwise maps, proper FC/LFE behavior, no audio gaps or artifacts around non-PCM ramp-rate handling, DRM audio-component ELD notifications mapping to the expected port, and suspend/resume keeping link and pin state coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/atihdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/eld.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/eld.c

## Purpose
Provides generic HDMI ELD retrieval, procfs display/update helpers, and PCM capability narrowing based on parsed ELD/SAD data for HDA HDMI codecs.

## Important APIs, Types, and Functions
`snd_hdmi_get_eld_size()` reads the HDA HDMI DIP ELD buffer size. `snd_hdmi_get_eld()` reads every byte with `AC_VERB_GET_HDMI_ELDD`, validates the ELD valid bit, checks for empty first-byte data, handles a zero-size ASUS workaround by forcing 128 bytes, and returns the filled buffer and size. Under `CONFIG_SND_PROC_FS`, `snd_hdmi_print_eld_info()` prints monitor state, pin/device/converter NIDs, and parsed ELD details, while `snd_hdmi_write_eld_info()` lets procfs input mutate selected monitor, connection, speaker, and SAD fields for debugging/testing. `snd_hdmi_eld_update_pcm_info()` intersects a PCM stream's rates, formats, max bits per sample, and channel maximum with sink capabilities from parsed SAD entries.

## Control Flow
ELD retrieval first asks the codec for the DIP ELD buffer size, validates it against fixed and maximum ELD sizes, then loops through bytes. If the graphics driver is concurrently updating ELD and the valid bit drops, or if byte zero is zero, retrieval aborts with `-EINVAL` so callers can repoll. On success, the caller receives the exact ELD size. Procfs print exits early when ELD is invalid; write scans `name value` lines and updates only allowed parsed fields, including numbered `sadN_*` attributes. PCM update starts from mandatory basic audio stereo support, folds in all SAD rates/channels/LPCM bit depths, then restricts the codec stream descriptor to the sink-supported subset.

## State and Persistence Behavior
The file mostly operates on caller-owned `struct hdmi_eld`, `struct snd_parsed_hdmi_eld`, and `struct hda_pcm_stream` objects. `snd_hdmi_write_eld_info()` mutates in-memory ELD/debug state exposed by procfs but does not write sink EDID or hardware ELD registers. `snd_hdmi_eld_update_pcm_info()` destructively narrows the supplied PCM stream fields, so callers must start from codec capabilities before applying sink restrictions.

## Dependencies and Integration Points
It depends on the HDA codec verb interface, ALSA HDMI ELD parser/types, CEA SAD constants, procfs info buffers when enabled, and `hda_local.h`. It is linked into the generic HDMI codec object by the HDMI Makefile and is used by HDMI codec implementations when monitor ELD changes or when user space inspects HDMI sink information.

## Risks
ELD can be transient while the graphics driver updates it, so callers must handle `-EINVAL` and retry rather than treating it as permanent absence. The zero-size workaround assumes 128 bytes and may mask firmware/controller defects. Procfs write support is powerful for testing but can create in-memory sink capabilities that do not match real hardware. PCM narrowing can over-restrict streams if applied repeatedly without resetting to base codec capabilities first.

## Test Signals
Tests should cover normal ELD reads, invalid-valid-bit repoll behavior, zero-size workaround, invalid size rejection, DVI/zero-first-byte handling, procfs print/write round trips for SAD fields, LPCM 20/24-bit promotion to S32_LE, channel/rate restriction from SAD data, and HDMI hotplug flows where ELD changes update PCM capabilities without stale limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/eld.c -->
