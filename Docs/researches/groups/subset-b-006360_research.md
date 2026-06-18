# sources/distributed-fs/ceph-client/sound/firewire subset-b-006360 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/amdtp-stream.h -->
# sources/distributed-fs/ceph-client/sound/firewire/amdtp-stream.h

Purpose: declares the shared AMDTP/CIP streaming abstraction used by ALSA FireWire audio drivers. It models packet descriptors, stream directions, CIP quirks, sampling frequency codes, PCM integration, and multi-stream `amdtp_domain` coordination.

Important APIs/types: `enum cip_flags`, `enum cip_sfc`, `struct pkt_desc`, `struct amdtp_stream`, `amdtp_stream_process_ctx_payloads_t`, `struct seq_desc`, and `struct amdtp_domain`. Public calls initialize/destroy streams, set parameters, update after bus changes, add PCM constraints, prepare/abort PCM, add streams to a domain, start/stop domains, and expose PCM pointer/ack callbacks.

Control flow and state: backends initialize an `amdtp_stream` with direction, CIP format, flags, and a payload callback, then configure rate/data-block shape before adding it to an `amdtp_domain`. Runtime state includes FireWire ISO context, packet buffers/descriptors, current DBC/SYT state, PCM buffer/period pointers, ready wait queues, and domain stream lists. Persistence is in-memory only and reset by destroy/stop paths.

Dependencies/integration: depends on Linux FireWire ISO contexts, ALSA PCM/runtime types, `packets-buffer.h`, and backend protocols such as AM824 or DOT. Risks center on protocol quirk flags, concurrency around `pcm` pointer updates, ready wait timeouts, and DBC/SYT discontinuity handling. Test signals are successful stream start/stop, PCM pointer monotonicity, no XRUN under bus reset recovery, and correct behavior for devices requiring unusual CIP flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/amdtp-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/Makefile -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/Makefile

Purpose: builds the BeBoB ALSA FireWire driver object `snd-bebob.o` from common command, stream, proc, MIDI, PCM, hwdep, vendor quirk, and probe modules.

Important APIs/types/functions: no C API, but the object list defines integration order for `bebob_command.o`, `bebob_stream.o`, `bebob_proc.o`, `bebob_midi.o`, `bebob_pcm.o`, `bebob_hwdep.o`, `bebob_terratec.o`, `bebob_yamaha_terratec.o`, `bebob_focusrite.o`, `bebob_maudio.o`, and `bebob.o`.

Control flow and state: Kbuild links these compilation units into a single module enabled by `CONFIG_SND_BEBOB`. There is no persistence or runtime state here.

Dependencies/integration: integrates with the kernel sound/firewire build and depends on symbols supplied by the listed files plus common FireWire audio modules. Risks are build coverage risks: missing a new source file here would omit vendor support or driver entry points. Test signals are successful kernel build with `CONFIG_SND_BEBOB=m/y` and module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.c

Purpose: provides the BeBoB driver entry point, FireWire ID matching, ALSA card allocation, device naming, vendor/model spec selection, probe/remove/update handling, and module registration.

Important APIs/functions: `bebob_probe`, `bebob_update`, `bebob_remove`, `bebob_card_free`, `name_device`, `detect_quirks`, `get_saffire_spec`, `check_audiophile_booted`, `snd_bebob_init`, and `snd_bebob_exit`. It also declares module parameters `index`, `id`, and `enable`, and a large `ieee1394_device_id` table mapping vendor/model pairs to `snd_bebob_spec`.

Control flow and state: probe chooses a spec from ID data, Focusrite Saffire name probing, or M-Audio bootloader checks. It allocates an ALSA card, stores `struct snd_bebob`, names the card from CSR/register data, detects quirks, discovers streams, initializes duplex streaming, creates proc/MIDI/PCM/hwdep interfaces, and registers the card. Remove blocks until ALSA character devices close through `snd_card_free`. Bus update only refreshes FCP state, intentionally avoiding stream update because BeBoB bus resets cause packet discontinuity expected to surface as XRUN.

Dependencies/integration: integrates FireWire core driver registration, ALSA card lifecycle, BeBoB stream/PCM/MIDI/hwdep helpers, FCP, and M-Audio firmware loading. Risks include device table specificity, bootloader/spec misclassification, card index bitmap cleanup, and the M-Audio scheduled bus reset workaround. Test signals include matching known devices, successful card registration, correct longname/GUID, firmware cue behavior, and XRUN/reprepare behavior across bus resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.h -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.h

Purpose: central BeBoB internal header defining driver state, register addresses, stream formation/spec abstractions, AV/C BridgeCo command interfaces, and cross-file prototypes.

Important APIs/types: `struct snd_bebob`, `struct snd_bebob_stream_formation`, `snd_bebob_clock_spec`, `snd_bebob_rate_spec`, `snd_bebob_meter_spec`, `snd_bebob_spec`, `enum snd_bebob_clock_type`, `enum snd_bebob_quirk`, and BridgeCo plug direction/mode/unit/type enums. Inline helpers read BeBoB info registers and fill BridgeCo plug addresses.

Control flow and state: `struct snd_bebob` owns the ALSA card, FireWire unit, mutex/spinlock, selected spec, quirks, MIDI port counts, two AMDTP streams, two CMP connections, per-rate stream formation caches, sync input plug, hwdep lock state, optional M-Audio special context, and an AMDTP domain. State is runtime-only and torn down by ALSA private free.

Dependencies/integration: includes ALSA core/PCM/rawmidi/hwdep, FireWire core/constants, common FireWire helpers, FCP, packets buffers, ISO resources, AM824, and CMP. Risks are ABI-like internal coupling: every BeBoB source assumes these fields and specs remain consistent. Test signals include compile-time coverage of all extern specs and runtime stream discovery filling formation and MIDI fields before PCM/MIDI creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_command.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_command.c

Purpose: implements AV/C audio selector and BridgeCo extension command helpers used for BeBoB clock routing, plug discovery, stream format discovery, channel mapping, and vendor quirks.

Important APIs/functions: `avc_audio_set_selector`, `avc_audio_get_selector`, `avc_bridgeco_get_plug_type`, `avc_bridgeco_get_plug_ch_count`, `avc_bridgeco_get_plug_ch_pos`, `avc_bridgeco_get_plug_section_type`, `avc_bridgeco_get_plug_input`, and `avc_bridgeco_get_plug_strm_fmt`.

Control flow and state: each helper builds an AV/C command buffer, calls `fcp_avc_transaction`, checks response length/status (`NOT IMPLEMENTED`, `REJECTED`, `IN TRANSITION`), extracts the requested field, and frees temporary memory. It maintains no persistent state; callers own retry policy and interpretation.

Dependencies/integration: depends on `fcp_avc_transaction`, BridgeCo address fill helpers, and standard AV/C response codes. It feeds `bebob_stream.c` discovery and vendor files such as M-Audio/Terratec/Yamaha. Risks include fixed command lengths, variable FCP response length handling, strict response byte masks, and transient `-EAGAIN` behavior. Test signals are successful plug type/count/channel/format reads on supported devices and graceful `-ENOSYS`/`-EINVAL` for unsupported command variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_focusrite.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_focusrite.c

Purpose: supplies Focusrite Saffire and Saffire Pro BeBoB specs for clock source, sampling rate, and meter handling using Focusrite-specific register addresses.

Important APIs/functions: `saffire_read_block`, `saffire_read_quad`, `saffire_write_quad`, `saffirepro_both_clk_freq_get`, `saffirepro_both_clk_freq_set`, `saffirepro_both_clk_src_get`, `saffire_both_clk_src_get`, and `saffire_meter_get`. It exports `saffirepro_26_spec`, `saffirepro_10_spec`, `saffire_le_spec`, and `saffire_spec`.

Control flow and state: Focusrite specs bind function pointers into `snd_bebob_spec`. Pro devices read/write a rate selector register and map hardware clock-source fields to internal clock IDs. Non-Pro Saffire devices use generic BeBoB stream rate functions and read a smaller clock source register. Meter reads convert big-endian blocks and reorder Saffire LE channels.

Dependencies/integration: integrated from `bebob.c` device table and used by proc meter/clock reporting and PCM rate decisions. Risks include hard-coded offsets, clock source map divergence between Pro 10 and Pro 26, missing validation for unsupported external lock, and channel reorder assumptions. Test signals are correct proc clock/meter output, accepted rate changes without reboot for Pro devices, and no out-of-range clock ID returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_focusrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_hwdep.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_hwdep.c

Purpose: exposes the BeBoB ALSA hwdep device for FireWire node information, stream lock notifications, and userspace stream lock/unlock ioctls.

Important APIs/functions: `hwdep_read`, `hwdep_poll`, `hwdep_get_info`, `hwdep_lock`, `hwdep_unlock`, `hwdep_release`, `hwdep_ioctl`, optional `hwdep_compat_ioctl`, and `snd_bebob_create_hwdep_device`.

Control flow and state: reads wait on `hwdep_wait` until `dev_lock_changed`, then return `SNDRV_FIREWIRE_EVENT_LOCK_STATUS`. Ioctls return `snd_firewire_get_info` or set `dev_lock_count` to `-1` for userspace ownership. Release clears a stale userspace lock. State is protected by `bebob->lock`.

Dependencies/integration: uses ALSA hwdep and FireWire UAPI structures, and coordinates with PCM/MIDI open paths through `snd_bebob_stream_lock_try/release`. Risks include lock starvation between userspace and ALSA clients, missed wakeups if `dev_lock_changed` handling regresses, and compat ioctl coverage. Test signals are poll/read notification delivery, `SNDRV_FIREWIRE_IOCTL_GET_INFO` GUID/card correctness, and `LOCK` returning `-EBUSY` while streams are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_maudio.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_maudio.c

Purpose: implements M-Audio BeBoB firmware cueing, metering specs, and special firmware support for FireWire 1814/ProjectMix-style devices with nonstandard clock/control behavior.

Important APIs/functions: `snd_bebob_maudio_load_firmware`, `snd_bebob_maudio_special_discover`, `special_get_rate`, `special_set_rate`, `avc_maudio_set_special_clk`, `special_stream_formation_set`, mixer control callbacks for clock/source/digital interfaces/sync status, `special_meter_get`, and `normal_meter_get`. It exports several `maudio_*_spec` structures.

Control flow and state: bootloader devices are sent three little-endian cues after checking firmware date. Special devices allocate `special_params`, initialize clock settings through a vendor-dependent AV/C command, add ALSA controls, synthesize stream formations from digital format and model, and set MIDI port counts. Control callbacks reject changes while streams run, update cached parameters, notify sync control, and refresh formations.

Dependencies/integration: depends on AV/C selector helpers, FCP transactions, direct FireWire transactions, ALSA controls, proc metering, and BeBoB stream startup special cases. Risks include firmware date comparison, hard-coded meter sizes/offsets, cached special params diverging from hardware, rate-setting sleeps, and controls changing channel counts while clients have constraints open. Test signals are firmware boot bus reset, correct ALSA controls, metering reads, and stream formation changes when ADAT/SPDIF modes change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_maudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_midi.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_midi.c

Purpose: creates BeBoB ALSA rawmidi devices and connects rawmidi open/close/trigger operations to the shared duplex AMDTP stream.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_midi_substream_names`, and `snd_bebob_create_midi_devices`.

Control flow and state: open obtains the stream lock, reserves duplex resources at the current rate, increments `substreams_counter`, and starts streaming. Close decrements the counter, stops duplex streaming when last user exits, and releases the lock. Trigger installs or clears the rawmidi substream pointer in the AM824 TX/RX stream under spinlock.

Dependencies/integration: depends on `snd_bebob_stream_*`, AM824 MIDI trigger support, ALSA rawmidi, and detected `midi_input_ports`/`midi_output_ports`. Risks include substream counter imbalance if start fails, shared stream contention with PCM and hwdep locks, and port count discovery errors. Test signals are rawmidi device creation only when ports exist, duplex flags when both directions exist, and MIDI byte transfer during active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_pcm.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_pcm.c

Purpose: exposes a duplex ALSA PCM device for BeBoB streams, deriving rates/channels from discovered stream formations and bridging PCM callbacks to AMDTP domain operations.

Important APIs/functions: hardware rules `hw_rule_rate` and `hw_rule_channels`, `limit_channels_and_rates`, `pcm_init_hw_params`, PCM ops `pcm_open`, `pcm_close`, `pcm_hw_params`, `pcm_hw_free`, prepare/trigger/pointer/ack callbacks, and `snd_bebob_create_pcm_devices`.

Control flow and state: open locks the stream, installs hardware constraints, checks clock source, and may pin rate/period/buffer to current values when externally clocked or already reserved. `hw_params` reserves duplex resources and increments `substreams_counter`; `hw_free` decrements and stops when no users remain. Prepare starts duplex streaming and prepares the direction-specific AMDTP stream. Trigger only toggles the active PCM pointer.

Dependencies/integration: uses BeBoB stream formation tables, spec rate/clock callbacks, AM824 constraints, ALSA PCM managed vmalloc buffers, and `amdtp_domain` pointer/ack. Risks include constraints with empty formations, external-clock rate changes during open, counter imbalance, and error propagation from capture prepare. Test signals include valid channel/rate constraint pairs, JACK-style period consistency, XRUN recovery through prepare, and correct capture/playback pointer movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_proc.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_proc.c

Purpose: creates BeBoB `/proc/asound/.../firewire` diagnostic entries for clock, firmware, stream formation, and optional meter data.

Important APIs/functions: `proc_read_hw_info`, `proc_read_meters`, `proc_read_formation`, `proc_read_clock`, `add_node`, and `snd_bebob_proc_init`. `struct hw_info` mirrors the BeBoB information register layout.

Control flow and state: proc readers perform on-demand FireWire/register/spec reads and print text snapshots. Formation output reads cached TX/RX formation arrays. Meter output calls the model-specific meter spec. Nodes are registered under an ALSA card proc directory and are removed by card disconnect.

Dependencies/integration: depends on `snd_bebob_read_block`, spec rate/clock/meter callbacks, ALSA info APIs, and the stream discovery cache. Risks include endianness assumptions in packed hardware info, silent return on allocation/read failure, and meter label/channel count mismatches. Test signals are readable proc entries, plausible firmware/GUID values, formation rows matching PCM constraints, and model-specific meter output when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_stream.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_stream.c

Purpose: implements BeBoB stream discovery, clock/rate access, CMP connection setup, AMDTP parameterization, duplex start/stop/reserve, and stream lock state.

Important APIs/functions: `snd_bebob_stream_get_rate`, `snd_bebob_stream_set_rate`, `snd_bebob_stream_get_clock_src`, `snd_bebob_stream_discover`, `snd_bebob_stream_init_duplex`, `snd_bebob_stream_reserve_duplex`, `snd_bebob_stream_start_duplex`, `snd_bebob_stream_stop_duplex`, `snd_bebob_stream_destroy_duplex`, `snd_bebob_stream_lock_try/release`, plus helpers for formation parsing, channel mapping, MIDI detection, and sync input discovery.

Control flow and state: discovery reads BridgeCo plug info, stream format entries, external MIDI plugs, and optional MSU sync input. Reserve checks for external CMP use, gets/sets rate, reserves both CMP connections, configures AM824 streams, and records period/buffer events. Start establishes both CMP connections, adds streams to the AMDTP domain, starts packet processing with replay and quirk-specific skip cycles, optionally reasserts M-Audio special rate, then waits for readiness. Stop tears down domain/CMP/resources when `substreams_counter` reaches zero.

Dependencies/integration: uses AV/C helpers, CMP, AM824, FireWire ISO resources, PCM/MIDI counters, and vendor specs. Risks include channel-position parsing, external applications holding CMP connections, devices needing both connections, DBC quirks, long startup delays, and rate changes while clients are open. Test signals are successful stream discovery, no cache mismatch, duplex readiness, correct MIDI/PCM maps, and stable bus-reset/XRUN recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_terratec.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_terratec.c

Purpose: provides the TerraTec PHASE 88 Rack BeBoB spec with custom clock-source detection.

Important APIs/functions: `phase88_rack_clk_src_get` and exported `phase88_rack_spec`; it also defines `phase88_rack_clk_src_types` and a generic rate spec using BeBoB stream get/set functions.

Control flow and state: the clock getter reads two AV/C audio selectors, one for external enable and one for word-clock enable, then maps the combination to internal, S/PDIF external, or word-clock external source IDs. No persistent state is stored in this file.

Dependencies/integration: selected from `bebob.c` ID table and consumed by `snd_bebob_stream_get_clock_src`, proc clock display, and PCM external-clock constraints. Risks include selector function block IDs changing across firmware and ambiguous external/word selector combinations. Test signals are correct proc clock source and rate constraints under internal, S/PDIF, and word-clock modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_terratec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_yamaha_terratec.c -->
# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_yamaha_terratec.c

Purpose: supplies the shared Yamaha GO44/GO46 and TerraTec PHASE 24/X24 BeBoB spec with clock source lookup and generic rate handling.

Important APIs/functions: `clk_src_get` and exported `yamaha_terratec_spec`; it defines clock source types for internal and S/PDIF external sources.

Control flow and state: the clock getter reads AV/C selector function block 4, validates the returned index, and maps it to a clock type. Rate get/set use the generic BeBoB stream helpers. The file stores no runtime state.

Dependencies/integration: selected from the BeBoB ID table and used by clock/rate/proc/PCM paths. The comments document device behavior at 192 kHz and interactions with mixer transactions. Risks include noisy high-rate operation if asynchronous mixer traffic continues, selector ID assumptions, and unsupported clock IDs. Test signals are valid clock reporting, successful high-rate streaming with mixer traffic minimized, and rate constraints matching discovered formations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_yamaha_terratec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/cmp.c -->
# sources/distributed-fs/ceph-client/sound/firewire/cmp.c

Purpose: implements IEC 61883-1 Connection Management Procedures for point-to-point FireWire isochronous connections used by drivers such as BeBoB.

Important APIs/functions: `cmp_connection_init`, `cmp_connection_check_used`, `cmp_connection_destroy`, `cmp_connection_reserve`, `cmp_connection_release`, `cmp_connection_establish`, and `cmp_connection_break`. Internal helpers compute MPR/PCR addresses, perform compare-swap PCR modification, encode oPCR speed/overhead, and validate plug availability.

Control flow and state: init reads iMPR/oMPR, validates plug index, initializes ISO resources, and records max speed. Reserve allocates channel/bandwidth. Establish compare-swaps the target iPCR/oPCR to set point-to-point connection/channel/speed, retrying resource update on bus reset. Break clears broadcast/P2P bits and leaves resources for the caller to release. State is held in `cmp_connection` and protected by its mutex.

Dependencies/integration: depends on FireWire CSR register constants, `snd_fw_transaction`, `fw_iso_resources`, and device max speed. Risks include PCR races with other hosts, bus-reset generation handling, oPCR overhead encoding limits, stale `last_pcr_value`, and resource leaks if callers skip release. Test signals are successful reserve/establish/break/release cycles, `-EBUSY` when plug is in use, and recovery after `-EAGAIN` bus reset updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/cmp.h -->
# sources/distributed-fs/ceph-client/sound/firewire/cmp.h

Purpose: declares the CMP connection manager interface for FireWire audio drivers that need to reserve ISO resources and program target plug control registers.

Important APIs/types: `enum cmp_direction`, `struct cmp_connection`, and public functions `cmp_connection_init`, `cmp_connection_check_used`, `cmp_connection_destroy`, `cmp_connection_reserve`, `cmp_connection_release`, `cmp_connection_establish`, and `cmp_connection_break`.

Control flow and state: callers initialize with a FireWire unit, input/output direction, and PCR index; reserve bandwidth/channel; establish the target PCR; later break and release. `struct cmp_connection` persists connection/resource state including actual speed, allocated resources, last PCR value, max speed, and mutex.

Dependencies/integration: includes `iso-resources.h` and Linux mutex/types. Risks are misuse order, such as destroying while connected or establishing without reserved resources, and shared access to the underlying target plug. Test signals are compile-time users in BeBoB and runtime connection state tracking through `connected` and ISO resource allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/cmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/Makefile -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/Makefile

Purpose: builds the DICE ALSA FireWire driver object `snd-dice.o` from transaction, stream, proc, MIDI, PCM, hwdep, core probe, and vendor detector modules.

Important APIs/types/functions: no C API, but the object list wires `dice-transaction.o`, `dice-stream.o`, `dice-proc.o`, `dice-midi.o`, `dice-pcm.o`, `dice-hwdep.o`, `dice.o`, and detector files for TC Electronic, Alesis, extension, Mytek, PreSonus, Harman, Focusrite, Weiss, and TEAC.

Control flow and state: Kbuild links all components when `CONFIG_SND_DICE` is enabled. It stores no runtime state.

Dependencies/integration: integrates with kernel sound/firewire build and all common DICE helpers. Risks are omission of detector objects from the module when adding device support. Test signals are successful module build and resolution of all detector symbols referenced from `dice.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-alesis.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-alesis.c

Purpose: supplies stream format detection for Alesis iO14/iO26 and MasterControl DICE devices using static per-mode channel maps.

Important APIs/functions: `snd_dice_detect_alesis_formats` and `snd_dice_detect_alesis_mastercontrol_formats`.

Control flow and state: iO detection reads current TX audio channel count to distinguish smaller and larger models, copies a static TX map, sets RX channels to 8 for all modes, and enables one MIDI port. MasterControl fills explicit two-stream channel counts for low/middle/high modes and two MIDI ports on both streams.

Dependencies/integration: called through `dice.c` ID table during probe before PCM/MIDI creation. Risks include model inference from current TX channel count, firmware variants with different stream layouts, and unsupported high-rate second stream assumptions. Test signals are formation proc output matching hardware, creation of expected PCM devices/ports, and no `keep_dual_resources` cache mismatch at stream reserve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-alesis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-extension.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-extension.c

Purpose: detects DICE stream formats through the TCAT application protocol extension used by TCD2210/2220-class firmware.

Important APIs/functions: `snd_dice_detect_extension_formats`, `detect_stream_formats`, `read_stream_entries`, and `read_transaction`.

Control flow and state: the detector reads the extension section pointer table at `DICE_EXT_APP_SPACE`, rejects layouts with duplicate section offsets as unsupported/fallback, then reads stream configuration entries from the current/application section. For each supported rate mode implied by clock capabilities, it reads TX/RX stream counts and per-stream audio/MIDI counts into `dice->tx/rx_pcm_chs` and `tx/rx_midi_ports`.

Dependencies/integration: used as a preferred generic detector from `snd_dice_stream_detect_current_formats` and for specific device IDs. Risks include relying on section index 6, ignoring unsupported rate modes based only on clock caps, duplicate offset fallback, and fixed entry sizes. Test signals are successful probe on extension-capable devices, correct low/mid/high formation proc rows, and fallback to current-format detection on `-ENXIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-extension.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-focusrite.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-focusrite.c

Purpose: provides a hard-coded stream format detector for the Focusrite Saffire Pro 40 TCD3070-CH DICE variant that lacks TCAT extension support.

Important APIs/functions: `snd_dice_detect_focusrite_pro40_tcd3070_formats`.

Control flow and state: fills stream 0 TX/RX channel counts for low and middle modes and sets MIDI ports. No FireWire reads are performed. The function leaves high-rate mode unsupported by zero counts.

Dependencies/integration: selected by `dice.c` for the Focusrite model ID quirk. Risks include possible typo-like assignment of MIDI ports to index 1 for middle mode while PCM stays on stream 0, and lack of support for other Pro 40 firmware variants. Test signals are correct low/middle PCM device constraints and MIDI port availability on the physical device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-focusrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-harman.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-harman.c

Purpose: supplies fixed format detection for the Lexicon I-ONYX FW810S Harman DICE device.

Important APIs/functions: `snd_dice_detect_harman_formats`.

Control flow and state: for low and middle rate modes, it sets first TX stream to 12 PCM channels plus one MIDI port and first RX stream to 10 PCM channels plus one MIDI port. High mode remains unsupported.

Dependencies/integration: selected by the Harman entry in `dice.c`. Risks include limited coverage to frequencies up to 96 kHz and dependence on comments for hardware capabilities. Test signals are proc formation low/middle rows, expected PCM constraints, and successful reserve without cache mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-harman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-hwdep.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-hwdep.c

Purpose: exposes the DICE ALSA hwdep interface for node info, stream lock state, userspace locking, and DICE notification events.

Important APIs/functions: `hwdep_read`, `hwdep_poll`, `hwdep_get_info`, `hwdep_lock`, `hwdep_unlock`, `hwdep_release`, `hwdep_ioctl`, optional compat ioctl, and `snd_dice_create_hwdep`.

Control flow and state: read waits until either `dev_lock_changed` or `notification_bits` is set, then returns a lock-status event or `SNDRV_FIREWIRE_EVENT_DICE_NOTIFICATION` and clears the consumed flag. Ioctls expose FireWire card/GUID/name info and set/clear userspace lock ownership. State is spinlock-protected.

Dependencies/integration: receives notification bits from `dice-transaction.c`, coordinates with PCM/MIDI stream locks, and uses ALSA hwdep/UAPI. Risks include lost notifications if bits coalesce, userspace lock contention, and read starvation if both lock and notification events alternate. Test signals are poll readiness on device notifications, lock ioctl behavior, and correct `GET_INFO` metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-interface.h -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-interface.h

Purpose: documents and defines the DICE private FireWire register interface: section table, global registers, TX/RX stream registers, clock/status bits, and extended sync registers.

Important APIs/types: macro definitions for `DICE_PRIVATE_SPACE`, section offsets/sizes, `GLOBAL_OWNER`, `GLOBAL_NOTIFICATION`, clock select/status/capability fields, TX/RX register offsets, name sizes, AC3 fields, and extended sync fields.

Control flow and state: not executable code, but it defines how the driver reads section offsets, claims notification ownership, selects clock/rate, enables streams, programs ISO channels/speeds, and reads stream/channel/status data. State persists in device registers and is partly cleared by bus reset according to comments.

Dependencies/integration: consumed by DICE transaction, stream, proc, and detector files. Risks are register-version compatibility, all-quadlet byte-swapping of strings, write restrictions, and old firmware lacking later global fields. Test signals are successful subaddress validation, sane proc dumps, clock capability reads, and correct behavior after bus reset clears owner/enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-midi.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-midi.c

Purpose: creates DICE ALSA rawmidi devices and maps rawmidi operations to MIDI channels carried in AM824 streams.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_midi_substream_names`, and `snd_dice_create_midi`.

Control flow and state: creation scans all streams for maximum input/output MIDI ports, creates one rawmidi device if any exist, and sets duplex flags. Open locks and starts the shared duplex stream at current rate. Close decrements `substreams_counter` and stops when no users remain. Trigger installs rawmidi substreams on stream 0 AM824 MIDI ports.

Dependencies/integration: uses DICE stream reserve/start/stop and AM824 MIDI trigger support. Risks include only routing MIDI through stream 0 despite `MAX_STREAMS`, substream counter imbalance, and detector-provided port counts exceeding actual AM824 capability. Test signals are rawmidi port counts matching formation data and MIDI transfer while PCM is idle or active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-mytek.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-mytek.c

Purpose: supplies fixed stream formats for the Mytek Stereo 192 DSD-DAC DICE device.

Important APIs/functions: `snd_dice_detect_mytek_formats` and `struct dice_mytek_spec`.

Control flow and state: copies static TX/RX channel maps into the device state for all rate modes, with 8 capture channels and 4 playback channels on stream 0, no second stream, and no MIDI ports.

Dependencies/integration: selected by `dice.c` for Mytek model ID. Risks include incomplete coverage of other Mytek FireWire products and assumptions about native DSD presentation through PCM channel counts. Test signals are expected PCM constraints across 44.1-192 kHz and no rawmidi device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-mytek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-pcm.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-pcm.c

Purpose: exposes DICE PCM devices, one per supported stream index, with dynamic constraints derived from detected low/middle/high channel maps and clock capabilities.

Important APIs/functions: `dice_rate_constraint`, `dice_channels_constraint`, `limit_channels_and_rates`, `init_hw_info`, PCM ops `pcm_open`, `pcm_close`, `pcm_hw_params`, `pcm_hw_free`, prepare/trigger/pointer/ack callbacks, and `snd_dice_create_pcm`.

Control flow and state: open locks streams, sets AM824 constraints, and pins rate/period/buffer when externally clocked or already reserved; high-rate dual-wire mode adjusts period/buffer units. `hw_params` reserves duplex resources and increments `substreams_counter`. Prepare starts all required DICE streams and prepares the selected AMDTP stream. Trigger toggles PCM pointer only for the selected stream.

Dependencies/integration: depends on DICE format detection arrays, transaction clock source/rate reads, stream reserve/start, AM824, ALSA PCM, and AMDTP domain pointer/ack. Risks include a capture prepare path returning 0 even if stream start fails, empty channel maps producing invalid constraints, dual-wire period scaling, and external-clock changes. Test signals are per-device PCM creation, valid constraints for each rate mode, high-rate playback/capture without underruns, and pointer/ack correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-presonus.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-presonus.c

Purpose: supplies fixed stream format detection for the PreSonus FireStudio DICE device.

Important APIs/functions: `snd_dice_detect_presonus_formats` and `struct dice_presonus_spec`.

Control flow and state: reads the model ID from the unit directory, matches it against a small table, copies low/middle TX/RX channel maps, and enables one MIDI port on stream 0 when supported. High mode is left unsupported.

Dependencies/integration: selected by the PreSonus ID entry in `dice.c`. Risks include typo in the internal spec name only affecting readability, limited model table, and lack of high-rate channel support. Test signals are correct formation proc output, PCM device creation for two streams, and MIDI device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-presonus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-proc.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-proc.c

Purpose: creates DICE proc diagnostics for raw DICE register state and detected stream formation tables.

Important APIs/functions: `dice_proc_read_mem`, `dice_proc_fixup_string`, `dice_proc_read`, `dice_proc_read_formation`, `add_node`, and `snd_dice_create_proc`.

Control flow and state: proc reads fetch the section table and selected global/TX/RX/ext-sync registers, byte-swap quadlets, fix DICE string endianness, and print clock, enable, status, stream, AC3, and sync details. Formation reads print cached TX/RX PCM/MIDI counts for each stream and rate mode. No persistent state is changed, except extended status reads may clear device slip bits per interface semantics.

Dependencies/integration: depends on DICE register macros, FireWire transactions, ALSA info APIs, and detected format caches. Risks include reading variable-sized sections with minimum assumptions, string byte order handling, and side effects of reading slip status. Test signals are readable `firewire/dice` and `firewire/formation` proc nodes with sane section offsets and channel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-stream.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-stream.c

Purpose: manages DICE duplex stream resources, rate mode selection, clock selection, ISO channel programming, global enable, bus reset update, and stream locking.

Important APIs/functions: `snd_dice_stream_get_rate_mode`, `snd_dice_stream_reserve_duplex`, `snd_dice_stream_start_duplex`, `snd_dice_stream_stop_duplex`, `snd_dice_stream_init_duplex`, `snd_dice_stream_destroy_duplex`, `snd_dice_stream_update_duplex`, `snd_dice_stream_detect_current_formats`, and lock helpers. Key internals include `select_clock`, `get_register_params`, `keep_resources`, `keep_dual_resources`, `start_streams`, and `finish_session`.

Control flow and state: reserve stops existing sessions when needed, selects clock, reads stream register layout, configures AM824 parameters and ISO resources for each TX/RX stream, and records period/buffer events. Start updates resources after bus generation changes, programs TX/RX ISO channel registers and TX speed, sets global enable, starts the AMDTP domain with sequence replay, and waits briefly for readiness. Stop clears stream registers/global enable, stops the domain, and frees resources when no clients remain.

Dependencies/integration: uses DICE transactions/registers, FireWire ISO resources, AMDTP/AM824, clock notification completion, PCM/MIDI counters, and detector caches. Risks include high-rate dual-wire channel doubling, cache mismatch with hardware registers, short notification/readiness timeouts, bus reset reinitialization, and all-stream-or-none assumptions. Test signals include reserve/start/stop across rate changes, no cache mismatch logs, successful bus reset recovery, and correct high-rate channel mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-tcelectronic.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-tcelectronic.c

Purpose: supplies static stream format maps for TC Electronic DICE devices including Konnekt and Impact/Digital Konnekt variants.

Important APIs/functions: `snd_dice_detect_tcelectronic_formats`, `struct dice_tc_spec`, and static specs for Desktop Konnekt 6, Impact Twin, Konnekt 8/24D/Live, Studio Konnekt 48, and Digital Konnekt x32.

Control flow and state: reads model ID from the unit directory, selects the matching static spec, copies TX/RX channel maps into the DICE state, and sets one MIDI port when the spec has MIDI. No device stream registers are read for channel counts.

Dependencies/integration: selected by multiple TC Electronic entries in `dice.c`. Risks include model table incompleteness, static maps diverging from firmware, and no validation against current device registers until reserve-time cache checks. Test signals are formation proc rows matching device manuals and successful stream reserve with no cache mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-tcelectronic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-teac.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-teac.c

Purpose: detects stream formats for Tascam/TEAC IF-FW/DM MkII DICE devices.

Important APIs/functions: `snd_dice_detect_teac_formats`.

Control flow and state: reads TX stream count and RX stream count from DICE registers, assigns 16-channel low/middle TX/RX stream 0 with MIDI, and enables stream 1 with 16 channels in low/middle modes when the device reports more than one stream. High mode remains unsupported.

Dependencies/integration: selected by the TEAC-specific ID entry in `dice.c`. Risks include assuming 16 channels for all reported streams, no high-rate support, and dependence on stream count reads before normal stream initialization. Test signals are correct one- or two-stream PCM device creation and reserve success on DM-3200/DM-4800 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-teac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-transaction.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-transaction.c

Purpose: provides DICE register transaction helpers, clock/rate reads, global enable control, notification callback registration, owner compare-swap, and subaddress discovery.

Important APIs/functions: `snd_dice_transaction_write`, `snd_dice_transaction_read`, `snd_dice_transaction_get_clock_source`, `snd_dice_transaction_get_rate`, `snd_dice_transaction_set_enable`, `snd_dice_transaction_clear_enable`, `snd_dice_transaction_init`, `snd_dice_transaction_reinit`, and `snd_dice_transaction_destroy`. Internal functions include `get_subaddr`, `dice_notification`, `register_notification_address`, `unregister_notification_address`, and `get_subaddrs`.

Control flow and state: init validates section offsets/sizes, checks DICE major version when available, registers a host address handler, and claims `GLOBAL_OWNER` by compare-swap. Notifications OR bits into `dice->notification_bits`, complete `clock_accepted` when appropriate, and wake hwdep. Enable writes are generation-fixed and update `global_enabled`. Destroy unregisters owner and address handler.

Dependencies/integration: uses FireWire transactions/address handlers, DICE register macros, hwdep wait queue, stream clock selection, and bus-reset reinit. Risks include owner races with other hosts, old firmware without capability registers, retry logic around `-EAGAIN`, notification bit coalescing, and generation mismatch. Test signals are successful probe owner claim, hwdep notification reads, clock accepted completion, and re-registration after bus reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-weiss.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-weiss.c

Purpose: supplies stream format maps for Weiss DICE devices including DAC, interface, archive player, ADC, and AFI models.

Important APIs/functions: `snd_dice_detect_weiss_formats` and `struct dice_weiss_spec`.

Control flow and state: reads model ID from the unit directory, selects a static spec table entry, and copies TX/RX channel maps. Most models use 2 channels in all rate modes; AFI1 uses 24/16/8 channels across low/middle/high. No MIDI ports are configured.

Dependencies/integration: selected by Weiss entries in `dice.c`. Risks include table coverage, comments documenting similar models, and no validation until reserve-time hardware register reads. Test signals are correct PCM channel constraints for each Weiss model and no rawmidi device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice-weiss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice.c -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice.c

Purpose: main DICE driver module implementing FireWire ID matching, DICE category validation, ALSA card setup, transaction/stream/proc/PCM/MIDI/hwdep initialization, bus reset handling, and module registration.

Important APIs/functions: `check_dice_category`, `check_clock_caps`, `dice_card_strings`, `dice_card_free`, `dice_probe`, `dice_remove`, `dice_bus_reset`, `alsa_dice_init`, and `alsa_dice_exit`. The `dice_id_table` maps many OUIs/models to detector functions.

Control flow and state: probe optionally validates GUID/category layout, allocates `struct snd_dice`, selects a detector from `driver_data` or generic current-format detection, applies high-rate double-frame quirks for M-Audio/Avid, initializes synchronization primitives, claims DICE transactions, checks clock caps, reads card strings, detects formats, initializes streams, creates proc/PCM/MIDI/hwdep interfaces, and registers the card. Bus reset re-registers notification ownership and forces streams stopped under mutex.

Dependencies/integration: integrates FireWire driver core, ALSA card lifecycle, DICE transaction/stream/detector modules, and common AM824 infrastructure. Risks include device table matching exceptions, GUID category assumptions, old firmware capabilities, double-wire disable quirks, and error cleanup through `snd_card_free`. Test signals include probe on typical and quirk devices, correct card strings, successful bus reset recovery, and detector-selected formation output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice.h -->
# sources/distributed-fs/ceph-client/sound/firewire/dice/dice.h

Purpose: central DICE internal header defining driver state, stream limits, rate modes, transaction wrappers, stream/PCM/MIDI/hwdep/proc prototypes, and detector prototypes.

Important APIs/types: `MAX_STREAMS`, `enum snd_dice_rate_mode`, `struct snd_dice`, `enum snd_dice_addr_type`, transaction inline wrappers for global/TX/RX/sync sections, `snd_dice_rates`, stream management prototypes, and detector function declarations.

Control flow and state: `struct snd_dice` persists card/unit references, register section offsets, clock capabilities, per-stream channel/MIDI maps, notification handler/generation/bits, hwdep lock state, ISO resources, AM824 streams, global enable flag, high-rate quirk flag, clock completion, substream counter, and AMDTP domain. It is allocated as ALSA card private data and freed through card private cleanup.

Dependencies/integration: includes ALSA, FireWire, AM824, ISO resources, common lib, and `dice-interface.h`. Risks are tight cross-file coupling and fixed `MAX_STREAMS` support despite some ASICs documenting more RX streams. Test signals are successful build across all DICE components and runtime consistency of channel arrays, resources, and streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/dice/dice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/Makefile -->
# sources/distributed-fs/ceph-client/sound/firewire/digi00x/Makefile

Purpose: builds the Digidesign Digi 002/003 family FireWire driver object `snd-firewire-digi00x.o`.

Important APIs/types/functions: no C API, but object composition includes `amdtp-dot.o`, `digi00x-stream.o`, `digi00x-proc.o`, `digi00x-pcm.o`, `digi00x-hwdep.o`, `digi00x-transaction.o`, `digi00x-midi.o`, and `digi00x.o`.

Control flow and state: Kbuild links the protocol-specific AMDTP DOT implementation with stream, ALSA surface, transaction, and probe code when `CONFIG_SND_FIREWIRE_DIGI00X` is enabled. There is no runtime state in this file.

Dependencies/integration: integrates with kernel sound/firewire build. Risks are object list omissions, particularly because `amdtp-dot.o` provides protocol callbacks used by stream code. Test signals are successful module build and symbol resolution for Digi00x stream/PCM/MIDI/hwdep helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/amdtp-dot.c -->
# sources/distributed-fs/ceph-client/sound/firewire/digi00x/amdtp-dot.c

Purpose: implements the Digi 002/003 custom AMDTP "DOT" protocol for PCM and MIDI payload processing on top of generic AMDTP streams.

Important APIs/functions: `amdtp_dot_init`, `amdtp_dot_set_parameters`, `amdtp_dot_reset`, `amdtp_dot_add_pcm_hw_constraints`, `amdtp_dot_midi_trigger`, and payload callbacks `process_ir_ctx_payloads`/`process_it_ctx_payloads`. Internal helpers include the reverse-engineered `dot_scrt`/`dot_encode_step`, PCM read/write/silence routines, MIDI packet read/write, and FIFO rate limiting.

Control flow and state: initialization selects incoming or outgoing payload callback and uses `CIP_NONBLOCKING | CIP_UNAWARE_SYT`. Parameter setup reserves one MIDI data channel plus PCM channels, sets AM824 FDF, records PCM channel count, and computes MIDI FIFO limits. Outgoing processing writes PCM or silence, applies the DOT byte-encoding state, and embeds MIDI bytes with port tags. Incoming processing copies PCM to ALSA buffers and dispatches MIDI bytes. `amdtp_dot_reset` clears encoder carry/index/offset state.

Dependencies/integration: uses generic AMDTP, ALSA PCM/rawmidi, `amdtp_rate_table`, and Digi00x stream code. Risks include protocol reverse-engineering assumptions, MIDI FIFO approximation, port tag handling for console MIDI, and buffer wrap logic. Test signals are clean 24-bit PCM playback/capture, no MIDI overruns, correct console/physical MIDI routing, and no artifacts after reset/start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/amdtp-dot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-hwdep.c -->
# sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-hwdep.c

Purpose: exposes the Digi00x ALSA hwdep interface for FireWire node info, stream lock notifications, userspace stream locking, and asynchronous device messages.

Important APIs/functions: `hwdep_read`, `hwdep_poll`, `hwdep_get_info`, `hwdep_lock`, `hwdep_unlock`, `hwdep_release`, `hwdep_ioctl`, optional compat ioctl, and `snd_dg00x_create_hwdep_device`.

Control flow and state: read waits until either `dev_lock_changed` or `msg` is set, then returns a lock-status event or `SNDRV_FIREWIRE_EVENT_DIGI00X_MESSAGE` and clears the consumed state. Ioctls expose FireWire metadata and userspace lock control. Release clears a lingering userspace lock. All shared event/lock state is protected by `dg00x->lock`.

Dependencies/integration: depends on async message delivery from transaction code, stream lock helpers used by PCM/MIDI, ALSA hwdep/UAPI, and FireWire device metadata. Risks include message coalescing into a single `u32`, lock contention with active ALSA streams, and missed wakeups. Test signals are poll/read on async messages, correct `GET_INFO`, and `LOCK`/`UNLOCK` behavior across active streams and process close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-midi.c -->
# sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-midi.c

Purpose: creates rawmidi devices for Digi00x physical MIDI ports and optional console/control-surface MIDI ports, wiring them to the DOT AMDTP streams.

Important APIs/functions: `midi_open`, `midi_close`, `midi_capture_trigger`, `midi_playback_trigger`, `set_substream_names`, `add_substream_pair`, and `snd_dg00x_create_midi_devices`.

Control flow and state: open locks and starts the shared duplex stream, increments `substreams_counter`, and unwinds on failure. Close decrements the counter, stops streams as needed, and releases the lock. Triggers map rawmidi device 0 substreams to physical ports and nonzero device to port 2 for console/control, then install or clear DOT MIDI substream pointers under spinlock. Creation always adds physical ports and adds console ports only for console models.

Dependencies/integration: depends on Digi00x stream management, DOT MIDI trigger support, ALSA rawmidi, and `is_console`. Risks include label/name inversion in `add_substream_pair` making UI names confusing, port 2 multiplexing assumptions, and substream counter handling on start failure. Test signals are expected rawmidi devices for rack versus console models and MIDI transfer on physical and control ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/firewire/digi00x/digi00x-midi.c -->
