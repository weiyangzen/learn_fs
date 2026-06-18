# Research: subset-b-006000

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h

Purpose: defines the user/kernel hardware-dependent ALSA control ABI for RME HDSPM cards, including MADI-family card discovery, metering, clock/sync state, LTC status, and matrix mixer access.

Important APIs and types: the public surface is the `SNDRV_HDSPM_IOCTL_*` ioctl set plus ABI structs `hdspm_peak_rms`, `hdspm_config`, `hdspm_ltc`, `hdspm_status`, `hdspm_version`, `hdspm_channelfader`, `hdspm_mixer`, and `hdspm_mixer_ioctl`. Enums encode card type, sample speed, sync states, MADI input/channel/frame formats, sync sources, and LTC format/frame/input status. `HDSPM_MAX_CHANNELS` and `HDSPM_MIXER_CHANNELS` fix the ABI at 64 channels.

Control flow: userspace opens the ALSA hwdep device and issues read-only ioctls to fetch current metering, configuration, timecode, status, version/add-on data, or mixer coefficients. `SNDRV_HDSPM_IOCTL_GET_MIXER` uses an indirect userspace pointer because the mixer matrix is too large for normal ioctl size encoding.

State and persistence: this header stores no state; it describes snapshots of live device registers and driver-maintained mixer state. Mixer, clocking, sync, and meter values are runtime device state, while firmware revision, card type, serial, and TCO add-on flags are hardware identity.

Dependencies and integration points: depends on Linux integer types and ioctl macros from the ALSA UAPI include chain. It integrates with the HDSPM ALSA driver, hwdep ioctl handling, pro-audio control tools, and userspace mixers that understand the 64x128-to-64 matrix format.

Risks and test signals: ABI risks are struct padding differences from `int`/enum fields, unchecked userspace mixer pointers, stale 64-channel assumptions, and confusion between single/double/quad speed channel availability. Test by compiling UAPI consumers on 32/64-bit, exercising every ioctl against MADI/AIO/AES32/RayDAT variants, validating meter array bounds, and reading mixer state under active streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h

Purpose: defines Intel AVS topology token IDs used by ALSA topology blobs to describe firmware manifests, libraries, audio formats, module configurations, pipelines, bindings, path templates, pins, kcontrols, init configs, and NHLT configs.

Important APIs and types: `enum avs_tplg_token` is the ABI. Token ranges are grouped by logical structure: manifest tokens `1..11`, libraries `101..102`, audio formats `201..209`, module base config `301..305`, module extended config `401..443`, pipeline config `1401..1406`, bindings `1501..1509`, pipelines `1601..1604`, modules `1701..1710`, path templates/paths `1801..2103`, pin formats `2201..2203`, kcontrols `2301`, init configs `2401..2403`, and NHLT configs `2501..2502`.

Control flow: topology authoring tools emit these IDs into private topology tuples; the Intel AVS ASoC driver parses the tuple stream and populates in-kernel AVS topology objects before creating firmware pipelines and modules.

State and persistence: no runtime state is stored here. The token numbers are persistent ABI values embedded in topology files and must remain stable across kernel and userspace topology-tool versions.

Dependencies and integration points: the header has no type dependency beyond standard enum syntax. It integrates with ALSA topology parsers, Intel AVS firmware module descriptions, NHLT endpoint data, and user/distribution-provided topology binaries.

Risks and test signals: high risks are renumbering tokens, reusing IDs with incompatible meaning, token aliases for conditional path templates sharing base IDs, and parser drift between topology tools and kernel. Test by loading representative AVS topologies, fuzzing tuple order/counts, checking unknown token rejection, and validating old topology blobs across driver updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/intel/avs/tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sb16_csp.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sb16_csp.h

Purpose: exposes the ALSA hwdep ABI for controlling the Creative Sound Blaster 16 ASP/AWE32 CSP, including microcode loading, supported modes, start parameters, state reporting, and pause/restart commands.

Important APIs and types: mode, load, sample-width, channel, rate, and state bitmasks define the CSP capability vocabulary. `snd_sb_csp_mc_header`, `snd_sb_csp_microcode`, `snd_sb_csp_start`, and `snd_sb_csp_info` describe microcode identity/payload, run format, and device state. Ioctls include `SNDRV_SB_CSP_IOCTL_INFO`, `LOAD_CODE`, `UNLOAD_CODE`, `START`, `STOP`, `PAUSE`, and `RESTART`.

Control flow: userspace queries CSP info, loads a bounded microcode image, starts the CSP in a compatible width/channel mode, then controls stop/pause/restart around DMA playback or capture. The load ioctl uses `_IOC()` manually because the microcode struct exceeds ioctl size-bit limits on some architectures.

State and persistence: loaded microcode, selected function, current run parameters, and state bits are driver/device runtime state. Microcode payloads are supplied by userspace and are not persisted by this header.

Dependencies and integration points: integrates with ALSA hwdep, legacy SB16/AWE hardware support, and userspace utilities that manage CSP codecs or QSound mode.

Risks and test signals: risks include large ioctl payload handling, architecture-specific ioctl encoding, microcode size validation, state-machine transitions during DMA, and legacy 16-bit field ABI preservation. Test load/unload/start/stop on supported hardware or emulation, invalid microcode lengths, concurrent pause/restart, and 32/64-bit ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sb16_csp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h

Purpose: defines the ALSA hwdep protocol ABI for Focusrite Scarlett 2nd/3rd/4th Gen, Clarett USB, and Clarett+ devices, centered on protocol versioning, reboot, flash segment selection, erase, and erase progress.

Important APIs and types: version macros encode major/minor/subminor into `SCARLETT2_HWDEP_VERSION`, with helpers to extract each component. Ioctls are `SCARLETT2_IOCTL_PVERSION`, `REBOOT`, `SELECT_FLASH_SEGMENT`, `ERASE_FLASH_SEGMENT`, and `GET_ERASE_PROGRESS`. `scarlett2_flash_segment_erase_progress` reports erase progress and block count.

Control flow: userspace first reads the protocol version, selects either the settings or firmware flash segment, triggers erase, polls progress until the complete sentinel, and may request device reboot after maintenance.

State and persistence: selected flash segment and erase progress are runtime driver/device state. The target flash contents are persistent on the hardware, making wrong segment selection or interrupted updates externally visible after reboot.

Dependencies and integration points: depends on Linux fixed-size types and ioctl definitions. It integrates with the ALSA Scarlett2 mixer/control driver and firmware/settings update utilities.

Risks and test signals: risks include destructive flash operations exposed through hwdep, version negotiation drift, segment ID validation, and progress sentinel handling. Test with unsupported versions, invalid segment IDs, erase/reboot permission paths, progress polling across disconnect, and ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h

Purpose: preserves the ALSA Emux/AWE SoundFont patch ABI compatible with OSS-era AWE drivers, including patch headers, sample and voice records, preset mapping, and hwdep ioctls.

Important APIs and types: `soundfont_patch_info` is the 16-byte operation header for load/open/close/replace/map/probe/remove operations. `soundfont_open_parm`, `soundfont_voice_parm`, `soundfont_voice_info`, `soundfont_voice_rec_hdr`, `soundfont_sample_info`, and `soundfont_voice_map` define patch, voice, sample, and mapping records. `snd_emux_misc_mode` supports miscellaneous port modes. Ioctls include version, load patch, reset/remove samples, memory availability, and misc mode.

Control flow: userspace sends a patch header through `SNDRV_EMUX_IOCTL_LOAD_PATCH`; the driver interprets `type`, `len`, and trailing data as voice records, sample descriptors/data, open/close commands, or preset maps. Sample memory and voice mappings are then used by the Emux wavetable engine.

State and persistence: the header defines an in-memory driver patch database: loaded samples, instruments, voice parameters, mappings, locks, and memory accounting. SoundFont data is not persisted by the kernel; userspace reloads it after device reset.

Dependencies and integration points: depends on `sound/asound.h` for ALSA UAPI context and endian selection. It integrates with ALSA sequencer/synth, Emux wavetable drivers, and old OSS-compatible SoundFont loaders.

Risks and test signals: risks include endian-specific patch key encoding, variable trailing payload length validation, ioctl number collision on `0x84`, signed range semantics for key/velocity/pan, and legacy struct layout preservation. Test loading multi-voice banks, replacing/removing samples, malformed lengths, endian builds, and memory exhaustion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h

Purpose: defines Intel Skylake DSP topology private-data constants and small ABI structs used by topology blobs to describe channel formats, module types, device/link kinds, scheduling pins, and algorithm parameters.

Important APIs and types: constants include private control types, max copier config size, queue limits, and UUID string size. Enums cover event types, channel configurations, module types, core affinity, pipe connection types, hardware connection, device type, interleaving, sample type, pin homogeneity, module parameter type, token direction, and tuple/data block type. `skl_dfw_algo_data` is a packed flexible-parameter blob for module algorithm data.

Control flow: ALSA topology private data carries these values; the Skylake ASoC topology parser decodes tuple/data blocks, configures module graphs, and passes packed parameter blobs to firmware during initialization, set, or bind phases.

State and persistence: no state lives in the header. Topology files persist these numeric values, and the kernel translates them into runtime DSP pipeline/module state.

Dependencies and integration points: depends on Linux types and integrates with `snd_sst_tokens.h`, Skylake/HDA DSP firmware, ALSA topology controls, and machine-driver topology files.

Risks and test signals: risks include ABI drift in enum numeric values, flexible-array bounds in `skl_dfw_algo_data`, channel-config aliases, and topology/parser mismatch for heterogeneous pins. Test old and new topology loads, invalid block sizes, module init/set/bind transitions, and firmware rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/skl-tplg-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_ar_tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/snd_ar_tokens.h

Purpose: defines Qualcomm AudioReach ASoC topology token IDs and constants for graph/subgraph/container/module descriptions, PCM format metadata, I2S interface configuration, logging, and module private data.

Important APIs and types: constants encode subgraph performance/direction/scenario, container capability/position/domain, PCM interleaving, and I2S word-select source. `ar_event_types` and kcontrol IDs identify DAPM/control behavior. `AR_TKN_*` macros define DAI, subgraph, container, module, connection, hardware-interface, format, and log tokens. `audioreach_module_priv_data` is a little-endian flexible config container tagged with `SND_SOC_AR_TPLG_MODULE_CFG_TYPE`.

Control flow: topology blobs emit AudioReach tokens; the ASoC AudioReach parser builds graph objects, resolves module port connections, configures endpoint interfaces, and passes packed private module config arrays to Qualcomm DSP services.

State and persistence: the header has no state. Token streams and private config blobs are persistent topology ABI, while instantiated subgraphs/containers/modules are runtime DSP state.

Dependencies and integration points: depends on Linux fixed-width and little-endian types. It integrates with ALSA topology, Qualcomm APM/GPR graph management, DSP firmware module IDs, DAI endpoint setup, and kcontrols.

Risks and test signals: risks include token renumbering, fixed eight-connection token expansion limiting graph fan-out, flexible-array length validation, little-endian parsing on all CPU types, and deprecated in/out port tokens. Test topology parsing for playback/record/voice graphs, invalid port references, format conversion, I2S endpoint variants, and malformed private data sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_ar_tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h

Purpose: defines Intel SST/Skylake topology token numbers for module UUIDs, pin/queue metadata, resources, formats, pipeline config, manifest module resources, A-state tables, and format config indices.

Important APIs and types: `enum SKL_TKNS` is the ABI. It includes tuple/block tokens, pin type and dynamic-pin flags, module resource fields (`MAX_MCPS`, pages, IBS/OBS), pipe and format tokens, module parameter/capability tokens, library names, power/D0i3/DMA tokens, pipeline config tokens, manifest module resource/interface tokens, A-state tokens, and `SKL_TKN_U32_FMT_CFG_IDX`. The misspelled `SKL_TKL_U32_D0I3_CAPS` is intentionally kept and aliased for ABI compatibility.

Control flow: topology private data is parsed into Skylake DSP pipeline and module descriptors; direction/pin-count tokens scope subsequent format tokens, while manifest tokens describe firmware module capabilities available for graph creation.

State and persistence: no state is stored in this header. Numeric tokens are persistent topology ABI values and may be embedded in shipped firmware/topology files.

Dependencies and integration points: ties to `skl-tplg-interface.h`, Intel SST/Skylake ASoC topology code, firmware manifests, and userspace topology compilers.

Risks and test signals: risks include changing enum order, removing the typo alias, parser ambiguity around direction-scoped format tokens, and old topology blobs with retired token expectations. Test multiple topology versions, manifest resource tables, D0i3 tokens, bad block sizes, and 32/64-bit topology-tool compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/snd_sst_tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h

Purpose: centralizes Sound Open Firmware ABI version constants, encoding/decoding helpers, compatibility tests, and magic numbers for IPC3 and IPC4 non-IPC data blobs.

Important APIs and types: `SOF_ABI_MAJOR`, `SOF_ABI_MINOR`, and `SOF_ABI_PATCH` define the current ABI version. `SOF_ABI_VER()`, `SOF_ABI_VERSION_MAJOR/MINOR/PATCH()`, and `SOF_ABI_VERSION_INCOMPATIBLE()` encode and compare the `MMmmmppp` 32-bit format. `SOF_ABI_MAGIC` and `SOF_IPC4_ABI_MAGIC` identify IPC3 and IPC4 data.

Control flow: topology and firmware blob parsers read an ABI/magic field, reject incompatible major versions, and use minor/patch to gate backward-compatible feature handling.

State and persistence: no runtime state. These constants are persisted in firmware, topology, and component private data.

Dependencies and integration points: depends on Linux types and is included by SOF topology and manifest headers, SOF drivers, and userspace tooling.

Risks and test signals: risks include incorrect version bumps for breaking changes, magic mixups between IPC3 and IPC4, and mask/shift errors. Test parsing old/new SOF topology blobs, incompatible major rejection, and tooling output matching kernel constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h

Purpose: defines the SOF firmware container file format: global header, module headers, block headers, block target memory types, and firmware signature/header ABI.

Important APIs and types: `snd_sof_fw_header` holds `"Reef"`, file size, module count, and header ABI. `snd_sof_mod_hdr` describes base firmware or loadable module sections and block count. `snd_sof_blk_hdr` describes individual IRAM/DRAM/SRAM/ROM/IMR/reserved blocks by type, payload size, and target offset. All layout structs are packed.

Control flow: the SOF driver validates the file signature/header ABI, iterates modules, then iterates blocks and copies each block payload to the memory area implied by the type and offset before starting firmware.

State and persistence: this describes persistent firmware image bytes on disk. Runtime state arises after the loader places blocks into DSP/host memory.

Dependencies and integration points: depends on Linux types and integrates with firmware_class loading, SOF platform loaders, DSP memory maps, and firmware build tools.

Risks and test signals: risks include trusting file/module/block sizes, integer overflow while walking packed blobs, negative enum values in packed ABI, and target offset validation. Test malformed firmware headers, truncated modules, unknown block types, multiple modules, and loader bounds on each target memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h

Purpose: defines generic SOF ABI headers and manifest TLV containers for non-IPC component data and topology manifest metadata.

Important APIs and types: `sof_abi_hdr` carries magic, type/parameter ID, payload size, ABI version, reserved words, and flexible `data[]`. `sof_manifest_tlv` is a little-endian TLV item. `sof_manifest` records ABI major/minor/patch, TLV count, and flexible items. `SOF_MANIFEST_DATA_TYPE_NHLT` identifies NHLT data payloads.

Control flow: topology/firmware parsers validate magic and ABI, dispatch payloads by `type`, and walk variable-size TLV items in the manifest to extract optional data such as NHLT.

State and persistence: no state in the header; the structs are serialized into topology or firmware data and become runtime component private data only after parsing.

Dependencies and integration points: depends on Linux integer and endian types. It integrates with SOF IPC3/IPC4 component params, topology manifests, NHLT endpoint data, and userspace SOF topology tooling.

Risks and test signals: risks include flexible-array length overflow, missing reserved-zero validation, little-endian TLV parsing, and ABI/magic mismatches. Test malformed TLV counts/sizes, IPC3 vs IPC4 data, NHLT extraction, and 32/64-bit packed layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h

Purpose: assigns SOF topology token IDs and kcontrol IDs for buffers, DAIs, schedulers, controls, audio-processing components, vendor DAI blocks, CAVS formats, copier options, and platform-specific endpoints.

Important APIs and types: the ABI is a set of `SOF_TKN_*` constants and `SOF_TPLG_KCTL_*` IDs. Token groups include buffer size/caps/flags, DAI type/index/direction, scheduler period/priority/core/domain/memory/direction, gain/volume/SRC/ASRC fields, component format/UUID/CPC/pins/bindings, Intel SSP/DMIC/HDA/ALH/CAVS/copier, i.MX SAI/ESAI/MICFIL, MediaTek AFE, AMD ACPDMIC/ACP I2S/ACP SoundWire, stream D0i3/pause flags, mute LED, and mixer type.

Control flow: topology compilers write these token IDs into ALSA topology private data; SOF topology parsers translate them into IPC3/IPC4 component, pipeline, DAI, scheduler, and kcontrol configuration before firmware graph creation.

State and persistence: no state is stored here. Token values are persistent ABI embedded in topology files and must remain stable. Some token IDs are intentionally retired or overlapping for backward compatibility/platform-specific scopes.

Dependencies and integration points: integrates with SOF topology tooling, ALSA ASoC topology, SOF IPC message construction, Intel/AMD/i.MX/MediaTek endpoint drivers, and firmware graph parsers.

Risks and test signals: risks include token collisions such as mixer/AMD ACPI2S ranges, retired token reuse, parser disagreement with topology configuration files, and platform token additions without ABI discipline. Test all supported platform topology blobs, unknown token handling, old ABI 3.x topologies, and generated IPC payload validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/tlv.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/tlv.h

Purpose: defines ALSA control TLV type IDs and convenience macros for constructing dB scale, dB min/max, linear, range, channel-map, and nested container TLV arrays.

Important APIs and types: `SNDRV_CTL_TLVT_*` constants classify TLV payloads. `SNDRV_CTL_TLVD_ITEM`, `SNDRV_CTL_TLVD_LENGTH`, and declaration macros build static `unsigned int` arrays. Offset constants identify type, length, min/max, mute, and step fields. `SNDRV_CTL_TLVD_DB_GAIN_MUTE` is the mute gain sentinel.

Control flow: drivers expose TLV arrays for mixer controls; userspace reads them through ALSA control APIs and interprets type/length/data records to display or map raw control values to dB/channel semantics.

State and persistence: no state is stored. TLV arrays are typically static driver metadata or generated control metadata.

Dependencies and integration points: integrates with ALSA control core, mixer applications, channel-map controls, and driver-defined static TLV tables.

Risks and test signals: risks include incorrect length/alignment, nested range ordering violations, signed dB value handling inside unsigned arrays, and macro misuse with non-constant arguments. Test mixer TLV reads, dB conversion in userspace, range validation, and compile-time construction across compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h

Purpose: defines the ALSA USB stream mmap/ioctl ABI used by low-latency USB audio streaming code to share stream configuration, packet ring metadata, and state with userspace.

Important APIs and types: `USB_STREAM_INTERFACE_VERSION` gates ABI version. `SNDRV_USB_STREAM_IOCTL_SET_PARAMS` accepts `usb_stream_config` with version, sample rate, period frames, and frame size. `usb_stream_packet` and `usb_stream` expose packet offsets/lengths, read/write sizes, period accounting, input packet ring indexes, split packet state, and `usb_stream_state`.

Control flow: userspace sets stream parameters, maps or reads shared stream state, follows output packet descriptors and input packet ring metadata, and reacts to state transitions from stopped/sync/ready/running/xrun.

State and persistence: `usb_stream` is live shared runtime state tracking scheduling, periods, idle sizes, synchronization packet, packet queues, and xruns. Nothing is persisted beyond the stream lifetime.

Dependencies and integration points: integrates with ALSA hwdep/PCM USB streaming, userspace JACK-style low-latency clients, and USB isochronous packet scheduling.

Risks and test signals: risks include flexible-array sizing, ring index races, version mismatch, xrun state handling, and ABI assumptions about `unsigned`/`int` widths. Test parameter negotiation, mmap size calculations, packet wrap/split behavior, xruns, and 32/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/usb_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/edid.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/edid.h

Purpose: provides the minimal UAPI EDID block wrapper used by legacy framebuffer/video interfaces.

Important APIs and types: `struct edid_info` contains a single 128-byte `dummy` array representing one base EDID block.

Control flow: drivers or legacy ioctls can pass a raw 128-byte EDID block through this struct without interpreting it in the header.

State and persistence: no state is stored. The bytes represent display-provided configuration data read at runtime from monitor firmware.

Dependencies and integration points: this UAPI header is included by the kernel wrapper `include/video/edid.h` and old framebuffer paths that need a stable EDID container.

Risks and test signals: risks are mainly legacy ABI expectations and the fixed single-block size not covering extension blocks. Test compile inclusion from userspace/kernel wrappers and EDID read paths that still expose `edid_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h

Purpose: defines the public ioctl ABI and display flag vocabulary for the SiS framebuffer driver and its companion userspace/X tooling.

Important APIs and types: public flags describe CRT2/LCD/TV/VGA routing, TV standards/interfaces, CRT1/CRT2 display types, and single/mirror/dual-view modes. `sisfb_info` reports card identity, memory heap, mode, version, capabilities, PCI location, panel/TV details, flags, POST state, and reserved expansion bytes. `sisfb_cmd` carries internal command requests/results, and `sis_memreq` supports framebuffer memory allocation/free interfaces. Ioctls include modern `SISFB_GET_INFO*`, retrace, automaximize, TV position, command, lock, and deprecated old numbers.

Control flow: userspace queries info size/info, reads vertical retrace, toggles panning behavior, adjusts TV output position, sends `SISFB_COMMAND`, or locks register access while coordinated tools manipulate state.

State and persistence: runtime state includes current display routing, video memory heap, viewport offset, TV position, lock state, and current flags. Hardware POST, panel delay, EMI, and special timing fields reflect probed hardware state, not persistent kernel data.

Dependencies and integration points: depends on Linux fixed-width types and asm ioctl macros. It integrates with the `sisfb` framebuffer driver, old X drivers, fb memory manager ioctls, and `sisfbctrl`-style utilities.

Risks and test signals: risks include duplicated/aliased flag bits, deprecated ioctl compatibility, large reserved ABI struct layout, command/result validation, and register-lock races. Test old and new ioctls, 32/64-bit layout, TV/LCD routing changes, lock/unlock behavior, and userspace tools expecting exact `SISFB_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h

Purpose: defines UAPI structs and flags for uvesafb userspace VBE helper tasks, virtual 8086 register state, and VBE information block layout.

Important APIs and types: `v86_regs` carries x86 register state for BIOS calls. Task flags `TF_VBEIB`, `TF_BUF_ESDI`, `TF_BUF_ESBX`, `TF_BUF_RET`, and `TF_EXIT` describe buffer and exit behavior. `uvesafb_task` carries flags, buffer length, and registers. `vbe_ib` is a packed VBE Info Block with signature, version, OEM pointers, capabilities, mode list, memory, reserved/OEM/misc data.

Control flow: the kernel framebuffer driver delegates VBE BIOS operations to a userspace helper, which receives a task, executes or emulates the BIOS call, and returns registers and optional buffers.

State and persistence: no kernel state is stored here. Task contents are transient; `vbe_ib` is display adapter firmware-provided capability data.

Dependencies and integration points: depends on Linux types and integrates with uvesafb, v86d-style helpers, x86 VBE BIOS conventions, and framebuffer mode selection.

Risks and test signals: risks include packed layout compatibility, pointer-like VBE far pointer fields in 32-bit values, buffer length validation, and helper/kernel protocol mismatch. Test helper round trips, VBE info parsing, mode list buffers, invalid flags, and non-x86 build isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h

Purpose: defines the `/dev/xen/evtchn` userspace ABI for binding, notifying, unbinding, resetting, restricting, and statically binding Xen event channels.

Important APIs and types: ioctl structs include `ioctl_evtchn_bind_virq`, `bind_interdomain`, `bind_unbound_port`, `unbind`, `notify`, `restrict_domid`, and `bind`. Ioctl numbers use `_IOC()` with type `'E'` and operation IDs `0..7`.

Control flow: userspace opens the event channel device, binds a VIRQ/interdomain/unbound/static port, waits for events via the file descriptor, notifies ports, unbinds ports, resets event buffers, or restricts future interdomain binds to one domid.

State and persistence: state is per file descriptor: bound ports, buffered pending events, error/reset condition, and an optional irreversible domid restriction. Event channels are runtime hypervisor/kernel resources, not persistent data.

Dependencies and integration points: depends on Xen public types such as `domid_t` from the include environment. It integrates with Xen control stacks, backend/frontend drivers in userspace, and event-channel hypercalls.

Risks and test signals: risks include stale bindings after restriction, domid validation, event buffer reset semantics, port lifetime on fd close, and ioctl compatibility. Test bind/notify/read/unbind, restriction behavior, static port errors, reset after overflow, and multi-domain access control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/evtchn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h

Purpose: defines the `/dev/xen/gntalloc` ABI for allocating local pages, granting them to another Xen domain, deallocating grant references, and configuring unmap notifications.

Important APIs and types: `ioctl_gntalloc_alloc_gref` takes domid, flags, count and returns an mmap offset plus flexible grant-reference IDs. `ioctl_gntalloc_dealloc_gref` releases a range by index/count. `ioctl_gntalloc_unmap_notify` configures byte clearing and/or event-channel notification on unmap. Flags include `GNTALLOC_FLAG_WRITABLE`, `UNMAP_NOTIFY_CLEAR_BYTE`, and `UNMAP_NOTIFY_SEND_EVENT`.

Control flow: userspace allocates grants, mmaps the returned offset, shares grant refs with a peer domain, optionally sets crash/unmap notification, and deallocates after peers stop using the pages.

State and persistence: per-device/file state tracks allocated pages, grant refs, mmap offsets, peer access, and unmap notifications. Pages are transient but may carry shared-memory protocol state while mapped.

Dependencies and integration points: depends on Linux types and Xen grant-table/event-channel mechanisms. It integrates with interdomain shared-memory protocols and robust mutex/close notification schemes.

Risks and test signals: risks include flexible-array count sizing, writable grant policy, deallocating while mapped by peers, notification overwrite behavior, and index/page offset validation. Test allocate/mmap/share/dealloc, invalid counts, notification clear/send paths, peer crash cleanup, and 32/64-bit ioctl layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h

Purpose: defines the `/dev/xen/gntdev` ABI for mapping foreign grant references, unmapping them, resolving mmap offsets, limiting grants, setting unmap notifications, copying grant segments, and exporting/importing grants through dma-buf.

Important APIs and types: `ioctl_gntdev_map_grant_ref`, `unmap_grant_ref`, `get_offset_for_vaddr`, `set_max_grants`, and `unmap_notify` define core mapping control. `gntdev_grant_copy_segment` and `ioctl_gntdev_grant_copy` describe local/foreign copy operations with per-segment status. dma-buf structs export refs to an fd, wait for release, import an fd to refs, and release imports. DMA flags select write-combine or coherent backing.

Control flow: userspace inserts grant refs into a mapping table, mmaps the returned opaque offset, uses or shares the memory, then munmaps before unmapping. Copy ioctls perform grant-table copy operations without persistent mappings. dma-buf ioctls bridge Xen grant memory with Linux dma-buf sharing.

State and persistence: state is per gntdev instance: mapping table entries, maximum grant limit, live VMAs, unmap notifications, copy status, exported/imported dma-buf references, and backing allocation type. No state persists after fd/release except peer-visible effects.

Dependencies and integration points: depends on Linux types and Xen grant types (`grant_ref_t`, `domid_t`) plus `__user` annotations. It integrates with Xen grant tables, mmap, dma-buf, graphics/Wayland use cases, and interdomain copy protocols.

Risks and test signals: risks include refs flexible-array sizing, requiring munmap before unmap, split local buffers across Xen page boundaries, per-segment status handling, dma-buf lifetime waits, and access-control to foreign grants. Test map/unmap/mmap-offset recovery, copy success/failure statuses, invalid mixed local source/dest segments, dma-buf export/import/release, and max grant limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h

Purpose: defines the privileged Xen control ABI exposed through `/proc/xen/privcmd` or equivalent device nodes for hypercalls, foreign memory mapping, device-model ops, restrictions, resource mapping, irqfd/ioeventfd, and PCI GSI lookup.

Important APIs and types: structs include `privcmd_hypercall`, `privcmd_mmap_entry`, `privcmd_mmap`, `privcmd_mmapbatch`, `privcmd_mmapbatch_v2`, `privcmd_dm_op_buf`, `privcmd_dm_op`, `privcmd_mmap_resource`, `privcmd_irqfd`, `privcmd_ioeventfd`, and `privcmd_pcidev_get_gsi`. Ioctls cover hypercall, mmap, mmapbatch/v2, device-model ops, restriction, resource mapping, irqfd/ioeventfd assignment/deassignment, and PCI GSI lookup.

Control flow: privileged userspace issues hypercalls with up to five args, maps foreign GFNs or resources into its address space, performs batched remaps with per-frame errors, submits device-model buffers, restricts the fd to a domid, and wires eventfds for IRQ or I/O event injection.

State and persistence: state includes per-fd restrictions, mapped VMAs, device-model/eventfd registrations, and resource mappings. Effects are runtime hypervisor/domain state and can affect guest memory/device emulation.

Dependencies and integration points: depends on Linux types/compiler annotations and Xen public `xen.h`. It integrates with Xen toolstacks, QEMU device models, dom0 control flows, foreign memory mapping, and eventfd-based emulation.

Risks and test signals: risks are high because this is a privileged hypervisor control surface: pointer validation, domid restriction enforcement, GFN/MFN naming legacy, batched error reporting, and eventfd deassignment races. Test hypercall argument copying, restricted fd behavior, mmapbatch partial failures, resource unmap, irqfd/ioeventfd assign/deassign, and compat ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/privcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufs.h

Purpose: defines core UFS protocol constants, descriptor/query offsets, UPIU transaction metadata, device feature bits, response structures, regulator/device info, and shared device state used by the UFS host controller stack.

Important APIs and types: key exports include UFS LUN/WLUN constants, task management codes, UPIU transaction/flag/attribute enums, query flag/attribute/descriptor IDs, descriptor parameter offsets, WriteBooster/HPB/HID/temperature feature bits, power modes, query opcodes/results, `utp_cmd_rsp`, `utp_upiu_rsp`, `ufs_vreg`, `ufs_vreg_info`, and `ufs_dev_info`.

Control flow: the UFS core builds UPIU commands using these enums, issues query requests to read/write flags, attrs, and descriptors, interprets response/result codes, configures feature bits such as WriteBooster/HPB/HID, and fills `ufs_dev_info` during probe for later PM, queue, RPMB, RTC, and exception handling.

State and persistence: protocol constants are static; `ufs_dev_info` is runtime cached device identity/capability state including write protection, LU counts, manufacturer/model/spec, queue depth, WriteBooster settings, RPMB/RTC/HID info, and device ID. Persistent state lives on the UFS device in descriptors, attributes, flags, flash, and RPMB.

Dependencies and integration points: depends on Linux bitops/types/time and UAPI SCSI BSG UFS definitions for UPIU wire structures. It integrates with SCSI UFS core, BSG passthrough, regulator handling, RPMB, power management, and device feature management.

Risks and test signals: risks include descriptor offset drift across UFS spec versions, endian/wire-structure assumptions, feature gating for pre-3.1 devices, query length validation, and WriteBooster/RPMB/RTC state transitions. Test probe descriptor parsing, query read/write attrs/flags, WLUN handling, feature enable/disable, RPMB multi-region info, and malformed device responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h

Purpose: defines UFS device vendor/model quirk matching and bit flags used to compensate for non-conformant or timing-sensitive UFS devices.

Important APIs and types: `STR_PRFX_EQUAL`, `UFS_ANY_VENDOR`, `UFS_ANY_MODEL`, and vendor IDs support matching. `ufs_dev_quirk` binds manufacturer/model to a quirk bitmask. Quirk bits cover DL NAC recovery, PA_TACTIVATE adjustments, regulator LPM delay, host PA_TACTIVATE/SAVECONFIGTIME/debug save config requirements, extended-feature probing, extra hibern8 time, and missing timestamp support.

Control flow: during probe or fixup, the UFS core matches device identity and sets `hba->dev_quirks`; later link startup, power-mode change, error handling, feature probing, and timestamp code checks these bits to alter behavior.

State and persistence: the header stores no state. Quirk state is runtime per device and derived from persistent manufacturer/model/spec behavior.

Dependencies and integration points: uses string matching and vendor IDs from UFS descriptors. It integrates with `ufshcd_fixup_dev_quirks()`, UniPro timing configuration, error recovery, LPM, and feature-detection paths.

Risks and test signals: risks include overly broad prefix matches, wrong vendor IDs, workaround interactions, and quirks masking real regressions. Test affected vendor devices, quirk table matching, NAC recovery timing, hibern8 entry/exit, timestamp fallback, and non-quirked devices for unchanged behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufs_quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshcd.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufshcd.h

Purpose: declares the central Linux UFS host-controller driver interface: HBA state, variant callback contracts, request/UPIU bookkeeping, power/clock/error state machines, MCQ queues, inline crypto hooks, WriteBooster/RTC/PM helpers, and exported core entry points.

Important APIs and types: major structs include `uic_command`, `ufshcd_lrb`, `ufs_query_req/res/query`, `ufs_dev_cmd`, `ufs_clk_info`, `ufs_pa_layer_attr`, `ufs_pwr_mode_info`, TX equalization records/settings, `ufs_hba_variant_ops`, `ufs_clk_gating`, `ufs_clk_scaling`, `ufs_event_hist`, `ufs_stats`, `ufs_hba_monitor`, `ufshcd_mcq_opr_info_t`, `ufs_hba`, and `ufs_hw_queue`. Enums define device commands, event types, PM operations/levels, link states, host states, PMC policy, host quirks, and host capabilities. Inline helpers cover link/device power state, DME wrappers, MMIO access, MCQ offsets, SG entry sizing, capability checks, and read/modify/write.

Control flow: platform drivers allocate/init an `ufs_hba`, provide variant ops, enable HCE/link startup, configure descriptors/queues, and expose SCSI devices. Requests use LRBs and UTRDs/command descriptors or MCQ SQ/CQ entries; completions update request state and statistics. PM flows map runtime/system/shutdown levels to device/link states, gate/ungate clocks, scale clocks via devfreq, enter/exit hibern8, and handle WriteBooster flushing. Error paths accumulate interrupt/UIC errors, schedule EH work, run link recovery or reset, and notify variant hooks. Device-management commands serialize through `dev_cmd.lock` and UIC commands through `uic_cmd_mutex`.

State and persistence: `ufs_hba` is the persistent in-kernel state for a controller while bound: MMIO/DMA descriptor bases, SCSI devices, current power/link state, outstanding request bitmaps, capabilities/quirks, event masks, workqueues, clocks/regulators, device info cache, WriteBooster and bkops flags, debugfs/fault injection, MCQ queues, PM QoS, exception counters, RPMB devices, and TX equalization parameters. Persistent data remains on the UFS device; the driver caches and controls it.

Dependencies and integration points: depends on block crypto, blk-mq, devfreq, debugfs, MSI, PM runtime, DMA direction, SCSI host/device, UniPro, UFS protocol, quirks, and UFSHCI descriptors. It integrates with platform-specific UFS drivers through `ufs_hba_variant_ops`, SCSI midlayer, block layer, runtime/system PM, regulators/clocks/OPP, debugfs, hwmon, fault injection, RPMB/OP-TEE, BSG, inline crypto, and MCQ interrupt resources.

Risks and test signals: high-risk areas are request tag/outstanding bitmap synchronization, UIC command serialization, PM vs error-handler races, clock gating/scaling active request counts, MCQ queue head/tail locking, inline crypto key handling and PRDT zeroization, variant callback ordering, and quirk/capability interactions. Test full probe/remove, SCSI I/O under runtime PM, suspend/resume/shutdown, link recovery, abort/task management, MCQ and legacy modes, WriteBooster flush/toggle, crypto I/O, fault injection, debugfs masks, and vendor variant callback matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshci.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufshci.h

Purpose: defines UFS Host Controller Interface register offsets, bit masks, queue register layout, crypto capability/config formats, UIC command constants, UTRD/UTMRD/CQE/PRDT descriptor layouts, and helper macros.

Important APIs and types: register enums cover core UFSHCI, crypto, MCQ config, SQ/CQ runtime, and interrupt aggregation registers. Masks describe capabilities, interrupts, controller status, UIC layer errors, AHIT, MCQ bits, and crypto config. Wire/DMA structs include `ufs_crypto_capabilities`, `ufs_crypto_cap_entry`, `ufs_crypto_cfg_entry`, `ufshcd_sg_entry`, `utp_transfer_cmd_desc`, `request_desc_header`, `utp_transfer_req_desc`, `cq_entry`, and `utp_task_req_desc`.

Control flow: the driver reads capabilities/version, enables the controller, programs descriptor base registers, rings transfer/task doorbells or MCQ tail pointers, services interrupts/CQ entries, decodes OCS/UIC error state, configures auto-hibern8, and optionally configures inline crypto.

State and persistence: the header defines hardware register and DMA descriptor layouts. Live state exists in controller registers, DMA rings/descriptors, crypto key slots, interrupt status, and MCQ pointers.

Dependencies and integration points: depends on Linux types and `ufs.h` for UPIU structures. It integrates tightly with `ufshcd.h`, SCSI UFS core, MMIO accessors, DMA mapping, MCQ, MSI/ESI, and blk-crypto.

Risks and test signals: risks include endian/bitfield layout in descriptor headers and CQ entries, static size assertions, register-version differences, MCQ vs legacy capability interpretation, PRDT size granularity, and crypto key material layout. Test register programming on UFSHCI 1.x-5.x controllers, DMA descriptor size/alignment, MCQ completion parsing, UIC error injection, interrupt aggregation, and crypto enable/config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/unipro.h -->
# sources/distributed-fs/ceph-client/include/ufs/unipro.h

Purpose: provides UniPro/M-PHY attribute IDs, timing conversion macros, power-mode enums, gear/lane tags, adaptation/equalization constants, and data/network/transport layer attribute definitions used by UFS link setup and tuning.

Important APIs and types: constants cover local/peer M-TX and M-RX attributes, common block attributes, PHY adapter attributes, vendor-specific attributes, TX equalization training, RX eye monitor, timeout defaults, data/network/transport layer attributes, CPort flags, and connection states. Enums define UFS operation mode, PA power modes, HS series, PWM/HS gears, lane count, UniPro versions, TX EQ presets, preshoot/deemphasis levels, and eye-mask types.

Control flow: UFS core and variant drivers issue DME get/set commands using these attribute IDs during link startup, power-mode negotiation, hibern8 entry/exit, gear changes, timeout setup, TX equalization, and error recovery.

State and persistence: no state is stored here. Attribute values live in host/device UniPro and M-PHY hardware registers and may be cached in `ufs_hba`.

Dependencies and integration points: uses bit macros from the broader kernel include environment and integrates with `ufshcd_dme_*()` wrappers, UFS power-mode negotiation, PHY drivers, vendor tuning code, and UFSHCI UIC commands.

Risks and test signals: risks include wrong attribute IDs, lane selector math, time unit conversion, gear-version gating, TX EQ bit packing, and vendor-specific attributes applied to the wrong PHY. Test DME get/set on local and peer attributes, HS/PWM gear switches, hibern8 timing quirks, TX equalization training, and UniPro version compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/unipro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/align.h -->
# sources/distributed-fs/ceph-client/include/vdso/align.h

Purpose: supplies vDSO-safe alignment macros for integer and pointer values without depending on broader kernel alignment headers.

Important APIs and types: `ALIGN`, `ALIGN_DOWN`, `__ALIGN_MASK`, `PTR_ALIGN`, `PTR_ALIGN_DOWN`, and `IS_ALIGNED` wrap kernel constant alignment helpers from `vdso/const.h`.

Control flow: vDSO and VVAR layout code uses these macros when sizing pages, aligning architecture data, and validating power-of-two boundaries.

State and persistence: no state; pure preprocessor helpers.

Dependencies and integration points: depends on `vdso/const.h` and the UAPI constant macros it exposes. It integrates with `vdso/datapage.h` and low-level arch vDSO code that cannot include heavy kernel headers.

Risks and test signals: risks include non-power-of-two `a`, pointer truncation through `unsigned long`, and type surprises in `IS_ALIGNED`. Test vDSO builds on 32/64-bit architectures and page/alignment calculations for VVAR symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/align.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/auxclock.h -->
# sources/distributed-fs/ceph-client/include/vdso/auxclock.h

Purpose: provides the generic auxiliary clock resolution hook for vDSO time code.

Important APIs and types: `aux_clock_resolution_ns()` is an always-inline helper returning `1` nanosecond.

Control flow: vDSO clock_getres-style code can call this helper for auxiliary clocks when reporting resolution.

State and persistence: no state; the value is a compile-time generic resolution.

Dependencies and integration points: includes UAPI time and type headers and integrates with auxiliary vDSO clock support referenced by `vdso/datapage.h`.

Risks and test signals: risk is inaccurate generic resolution if an architecture-specific auxiliary clock needs different semantics. Test aux clock getres behavior and architecture overrides where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/auxclock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/bits.h -->
# sources/distributed-fs/ceph-client/include/vdso/bits.h

Purpose: provides minimal `BIT()` and `BIT_ULL()` macros suitable for vDSO code.

Important APIs and types: `BIT(nr)` uses `UL(1)` and `BIT_ULL(nr)` uses `ULL(1)` from `vdso/const.h`.

Control flow: vDSO data masks such as supported clock IDs use these macros at compile time.

State and persistence: no state; pure macros.

Dependencies and integration points: depends on `vdso/const.h`; used by `vdso/datapage.h` and other small vDSO headers.

Risks and test signals: risks include undefined shifts for out-of-range bit numbers and type-width assumptions. Test compile-time masks for clock IDs on all vDSO architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/cache.h -->
# sources/distributed-fs/ceph-client/include/vdso/cache.h

Purpose: defines cacheline alignment helpers for vDSO data structures using architecture cache-size values.

Important APIs and types: `SMP_CACHE_BYTES` defaults to `L1_CACHE_BYTES` if not already provided, and `____cacheline_aligned` applies `__attribute__((__aligned__(SMP_CACHE_BYTES)))`.

Control flow: vDSO data page structs use this attribute to keep frequently-read data cacheline aligned for userspace fast paths.

State and persistence: no state; controls compile-time object layout.

Dependencies and integration points: depends on `asm/cache.h` and is used by `vdso/datapage.h`.

Risks and test signals: risks include missing architecture cache constants or changing struct layout shared with compat vDSO readers. Test vDSO layout and alignment assertions across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/include/vdso/clocksource.h

Purpose: defines vDSO clock mode identifiers, including architecture clock modes and the special time-namespace marker.

Important APIs and types: `enum vdso_clock_mode` includes `VDSO_CLOCKMODE_NONE`, optional `VDSO_ARCH_CLOCKMODES`, `VDSO_CLOCKMODE_MAX`, and `VDSO_CLOCKMODE_TIMENS = INT_MAX`.

Control flow: vDSO readers inspect `vdso_clock.clock_mode` to decide whether a clocksource is usable in userspace, requires arch-specific handling, or is a time namespace indirection that must use the slow path.

State and persistence: no state here; values are stored in the VVAR `vdso_clock` data page by kernel timekeeping code.

Dependencies and integration points: depends on `vdso/limits.h` and optionally `asm/vdso/clocksource.h` under generic gettimeofday. It integrates with `vdso/helpers.h` and generic vDSO time code.

Risks and test signals: risks include arch enum collisions and incorrect time namespace detection. Test clock_gettime fast/slow paths with and without time namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/const.h -->
# sources/distributed-fs/ceph-client/include/vdso/const.h

Purpose: exposes minimal typed constant macros for vDSO headers.

Important APIs and types: `UL(x)` and `ULL(x)` wrap `_UL()` and `_ULL()` from `uapi/linux/const.h`.

Control flow: other vDSO macros use these wrappers when building constants that must compile in kernel, user, or assembly-adjacent contexts.

State and persistence: no state.

Dependencies and integration points: depends on UAPI constant helpers and is included by vDSO bit/alignment/page helpers.

Risks and test signals: risks are low; test is broad vDSO compilation in C and assembly contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/datapage.h -->
# sources/distributed-fs/ceph-client/include/vdso/datapage.h

Purpose: defines the shared VVAR/vDSO data page layout for fast userspace time and getrandom support, including clock data, timestamps, namespace offsets, RNG state, architecture data, symbols, and page offsets.

Important APIs and types: `vdso_timestamp`, `vdso_clock`, `vdso_time_data`, and `vdso_rng_data` are the core shared layouts. Macros define accelerated clock masks (`VDSO_HRES`, `VDSO_COARSE`, `VDSO_RAW`, `VDSO_AUX`), clocksource slots, architecture data size/pages, VVAR symbols, and `enum vdso_pages` offsets. Optional arch structs come from `asm/vdso/time_data.h` and `asm/vdso/arch_data.h`.

Control flow: kernel timekeeping writes VVAR data under sequence counters; userspace vDSO code reads `vdso_u_time_data`, checks clock mode/seq, computes time from `cycle_last`, `mult`, `shift`, `mask`, and `basetime`, or follows time namespace offsets. getrandom vDSO code reads `vdso_u_rng_data` generation/readiness. Assembly linker scripts use `VDSO_VVAR_SYMS` to publish hidden VVAR symbols.

State and persistence: this is live shared kernel-to-userspace state: sequence counters, clocksource parameters, basetimes, namespace offsets, timezone/resolution, RNG generation/readiness, and arch data. It is not persistent across boot but is ABI-sensitive for 64-bit and compat readers.

Dependencies and integration points: depends on Linux/UAPI types, time definitions, bits, alignment, cache, page, and optional arch data. It integrates with kernel timekeeping, vDSO clock_gettime/gettimeofday/time, time namespaces, vDSO getrandom, linker scripts, and architecture-specific vDSO implementations.

Risks and test signals: high risks include struct layout changes affecting compat vDSO, sequence counter ordering, cacheline placement, time namespace slow-path markers, VVAR page offset changes, and hidden symbol relocation. Test vDSO time under concurrent updates, time namespaces, 32-bit compat, getrandom readiness/reseed, linker symbol placement, and all arch configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/datapage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/include/vdso/getrandom.h

Purpose: declares the vDSO getrandom state layout and architecture hooks for stack-safe ChaCha20 generation and the exported `__vdso_getrandom` entry point.

Important APIs and types: `vgetrandom_state` holds a union of buffered random bytes plus the next ChaCha key, a generation snapshot, current batch position, and reentrancy guard. `__arch_chacha20_blocks_nostack()` generates ChaCha20 output without stack writes, and `__vdso_getrandom()` is the arch-specific vDSO symbol delegating to common code.

Control flow: userspace passes an opaque per-thread state to `__vdso_getrandom`; the vDSO checks RNG generation/readiness, consumes buffered bytes, derives a new key/batch through the arch ChaCha routine, and falls back to syscall behavior when needed.

State and persistence: the opaque state is userspace-owned transient per-thread state. Its generation ties it to `vdso_rng_data`; it must be refreshed after kernel reseed. `in_use` prevents same-thread signal-handler reentrancy from reusing mutable state.

Dependencies and integration points: depends on Linux types and integrates with `vdso/datapage.h` RNG data, common vDSO getrandom implementation, arch ChaCha assembly/C code, and the getrandom syscall ABI.

Risks and test signals: risks include leaking stack data across fork, reentrancy races, stale generation handling, incorrect opaque state length, and flags behavior mismatch with syscall. Test fork/signal stress, reseed generation changes, small/large reads, invalid flags, fallback paths, and architecture ChaCha known-answer outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/gettime.h -->
# sources/distributed-fs/ceph-client/include/vdso/gettime.h

Purpose: declares vDSO time-related exported functions for clock_gettime, clock_getres, time, gettimeofday, and time64 variants.

Important APIs and types: function prototypes switch between `old_timespec32` and `__kernel_timespec` depending on 64-bit/compat build. Exports include `__vdso_clock_getres`, `__vdso_clock_gettime`, `__vdso_time`, `__vdso_gettimeofday`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`.

Control flow: libc resolves these vDSO symbols and calls them before falling back to syscalls; generic/arch vDSO implementations read VVAR data and fill caller-provided time structures.

State and persistence: no state in the header. Functions consume shared VVAR state from `vdso/datapage.h`.

Dependencies and integration points: depends on Linux time types and forward declarations. It integrates with libc symbol resolution, compat vDSO builds, and kernel-generated vDSO images.

Risks and test signals: risks include wrong prototype for compat builds, time32 overflow, and symbol ABI mismatch. Test 32-bit and 64-bit vDSO symbol calls, libc fallback behavior, Y2038/time64 paths, and invalid clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/gettime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/helpers.h -->
# sources/distributed-fs/ceph-client/include/vdso/helpers.h

Purpose: provides sequence-counter and memory-ordering helpers for safe lockless kernel writes and userspace vDSO reads of VVAR clock data, including time namespace detection.

Important APIs and types: helpers include `vdso_is_timens_clock`, `vdso_read_begin`, `vdso_read_begin_timens`, `vdso_read_retry`, `vdso_write_seq_begin`, `vdso_write_seq_end`, `vdso_write_begin_clock`, `vdso_write_end_clock`, `vdso_write_begin`, and `vdso_write_end`.

Control flow: writers mark seq odd, issue write barriers, update clock fields, issue another barrier, then mark seq even. Readers spin while seq is odd, use read barriers around data loads, and retry if the sequence changed. Time namespace pages use an odd seq with `VDSO_CLOCKMODE_TIMENS` to force a special slow path.

State and persistence: no owned state; helpers operate on `vdso_clock.seq` fields in shared VVAR pages.

Dependencies and integration points: depends on asm barriers, datapage, processor relax, and clocksource mode definitions. It integrates with kernel timekeeping writers and generic vDSO clock readers.

Risks and test signals: high risks are missing barriers, compiler tearing without `READ_ONCE`/`WRITE_ONCE`, infinite spin on time namespace pages, and updating only one clock slot. Test concurrent time updates, time namespace clocks, weak-memory architectures, and lockless reader retry rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/jiffies.h -->
# sources/distributed-fs/ceph-client/include/vdso/jiffies.h

Purpose: defines vDSO-safe tick duration constants derived from `HZ`.

Important APIs and types: `TICK_NSEC` computes nanoseconds per scheduler tick using `NSEC_PER_SEC` and `HZ`.

Control flow: low-resolution time helpers use `TICK_NSEC` to report clock resolution.

State and persistence: no state; compile-time constant.

Dependencies and integration points: depends on `asm/param.h` for `HZ` and `vdso/time64.h` units. It feeds `vdso/ktime.h`.

Risks and test signals: risks include rounding expectations for unusual `HZ` values. Test low-resolution clock_getres outputs across configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/jiffies.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/ktime.h -->
# sources/distributed-fs/ceph-client/include/vdso/ktime.h

Purpose: exposes low-resolution kernel time constants for vDSO-compatible code.

Important APIs and types: `LOW_RES_NSEC` and `KTIME_LOW_RES` both map to `TICK_NSEC`.

Control flow: vDSO getres paths can use these constants for coarse/low-resolution clocks.

State and persistence: no state.

Dependencies and integration points: depends on `vdso/jiffies.h`; integrates with generic vDSO time code.

Risks and test signals: risk is limited to mismatch with kernel clock resolution. Test clock_getres coarse/low-res outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/ktime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/limits.h -->
# sources/distributed-fs/ceph-client/include/vdso/limits.h

Purpose: provides a small limits header for vDSO code that cannot rely on full kernel or libc limits.

Important APIs and types: defines signed and unsigned min/max constants for short, int, long, long long, unsigned variants, and `UINTPTR_MAX`.

Control flow: other vDSO headers use these constants, notably `INT_MAX` for the time namespace clock mode marker.

State and persistence: no state.

Dependencies and integration points: standalone; integrates with `vdso/clocksource.h` and other low-level headers.

Risks and test signals: risks include type-size assumptions on unusual architectures. Test vDSO builds on 32/64-bit and compat configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/math64.h -->
# sources/distributed-fs/ceph-client/include/vdso/math64.h

Purpose: supplies vDSO-safe 64-bit arithmetic helpers used by time conversion code without pulling in broader kernel math helpers.

Important APIs and types: `__iter_div_u64_rem()` performs small iterative division with remainder. `mul_u64_u32_add_u64_shr()` computes `((a * mul) + b) >> shift`, using `unsigned __int128` where available or a split 32-bit fallback. `mul_u32_u32()` is provided in the fallback path.

Control flow: time conversion fast paths multiply cycle deltas by clocksource multipliers, add fractional bases, and shift to nanoseconds using these helpers.

State and persistence: no state; pure arithmetic.

Dependencies and integration points: depends on compiler support for overflow builtins and optional int128 config. It integrates with generic vDSO time calculations.

Risks and test signals: risks include shift edge cases, overflow carry handling, compiler optimizing iterative division into unsupported operations, and architecture int128 config mismatch. Test time conversion against kernel reference over max cycle deltas, overflow-protection configs, and compilers with/without int128.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/math64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/page.h -->
# sources/distributed-fs/ceph-client/include/vdso/page.h

Purpose: defines page size, shift, and mask constants for vDSO code based on `CONFIG_PAGE_SHIFT`.

Important APIs and types: `PAGE_SHIFT`, `PAGE_SIZE`, and `PAGE_MASK` are defined with special handling for 32-bit architectures to avoid wrong sign/width extension.

Control flow: VVAR page sizing and symbol placement use these constants when aligning data pages and computing offsets.

State and persistence: no state; compile-time layout constants.

Dependencies and integration points: depends on UAPI const macros and kernel config. It integrates with `vdso/datapage.h` and linker script page calculations.

Risks and test signals: risks include incorrect mask width on 32-bit and mismatch with architecture page size. Test VVAR layout on 4K/16K/64K page configs and compat builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/processor.h -->
# sources/distributed-fs/ceph-client/include/vdso/processor.h

Purpose: wraps architecture-specific vDSO processor helpers for non-assembly code.

Important APIs and types: the header itself defines no public function; it includes `asm/vdso/processor.h`, which typically provides `cpu_relax()` or related low-level helpers.

Control flow: vDSO spin-wait loops such as sequence-counter readers use arch processor helpers to wait efficiently.

State and persistence: no state.

Dependencies and integration points: depends on architecture vDSO processor headers and is used by `vdso/helpers.h`.

Risks and test signals: risks are missing arch implementations or unsafe inclusion in assembly. Test vDSO builds for every architecture and reader spin behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time.h -->
# sources/distributed-fs/ceph-client/include/vdso/time.h

Purpose: defines the time namespace offset structure shared by vDSO data pages.

Important APIs and types: `struct timens_offset` stores signed seconds and unsigned nanoseconds offsets.

Control flow: time namespace vDSO pages store per-clock offsets; namespace-aware vDSO code reads host time and applies these offsets.

State and persistence: instances are live VVAR state for time namespace mappings.

Dependencies and integration points: depends on UAPI Linux integer types and integrates with `vdso/datapage.h` and time namespace support.

Risks and test signals: risks include invalid nsec normalization and signed/unsigned arithmetic bugs. Test time namespace offsets for realtime/boottime/TAI and unaffected clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time32.h -->
# sources/distributed-fs/ceph-client/include/vdso/time32.h

Purpose: defines 32-bit legacy time types used by compat vDSO entry points.

Important APIs and types: `old_time32_t`, `old_timespec32`, and `old_timeval32` model signed 32-bit seconds plus nanosecond or microsecond subfields.

Control flow: 32-bit vDSO `clock_gettime`, `clock_getres`, and `gettimeofday` variants fill these structures for legacy ABIs.

State and persistence: no state; ABI type definitions only.

Dependencies and integration points: relies on `s32` being available from include context. It integrates with compat vDSO and Y2038 transition code.

Risks and test signals: risks include Y2038 overflow, missing type includes, and wrong prototype selection. Test 32-bit vDSO calls near overflow boundaries and compat libc behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time64.h -->
# sources/distributed-fs/ceph-client/include/vdso/time64.h

Purpose: provides time unit conversion constants for vDSO and lightweight kernel time code.

Important APIs and types: defines milliseconds, microseconds, nanoseconds, picoseconds, and femtoseconds per second or smaller unit constants.

Control flow: vDSO helpers and tick constants use these values for clock resolution and conversion.

State and persistence: no state; constants only.

Dependencies and integration points: standalone; used by `vdso/jiffies.h` and time conversion code.

Risks and test signals: low risk; test is compile-time use and unit conversion consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/unaligned.h -->
# sources/distributed-fs/ceph-client/include/vdso/unaligned.h

Purpose: provides vDSO-safe unaligned load/store macros that avoid undefined behavior and strict-aliasing assumptions.

Important APIs and types: `__get_unaligned_t(type, ptr)` copies bytes into an unqualified scalar temporary and returns it. `__put_unaligned_t(type, val, ptr)` copies a scalar temporary to an unaligned pointer.

Control flow: code parsing unaligned data in vDSO-compatible contexts can use these macros instead of type-punning or direct unaligned dereferences.

State and persistence: no state; memory helper macros only.

Dependencies and integration points: depends on compiler type helpers from `linux/compiler_types.h`. It integrates with arch/generic vDSO code needing portable unaligned access.

Risks and test signals: risks include misuse with non-scalar types, volatile/MMIO pointers, and sanitizer interactions. Test unaligned loads/stores under UBSAN/KASAN-compatible builds and strict-aliasing compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/include/vdso/vsyscall.h

Purpose: exposes architecture-specific vDSO/vsyscall update hooks to generic kernel timekeeping code.

Important APIs and types: includes `asm/vdso/vsyscall.h` and declares `vdso_update_begin()` and `vdso_update_end(flags)`.

Control flow: kernel writers call begin before updating vDSO data and end afterward, with architecture code using the returned flags to restore interrupt/preemption or mapping state as needed.

State and persistence: no owned state; hooks protect updates to shared vDSO/VVAR state.

Dependencies and integration points: depends on arch vDSO vsyscall headers and integrates with timekeeping update paths.

Risks and test signals: risks include mismatched begin/end flags, arch missing hooks, and update ordering with sequence counters. Test timekeeping updates, suspend/resume clocksource changes, and arch vDSO builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h -->
# sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h

Purpose: defines platform data and register/bit constants for the AT91/AT32 LCD Controller framebuffer driver.

Important APIs and types: `atmel_lcdfb_pdata` describes board-specific timing, backlight polarity, default bpp, LCD wiring mode, default control register values, power-control callback, default monitor specs, and power GPIO list. Register constants cover DMA frame buffers, LCD controller timing/configuration, FIFO, dither/palette, power, contrast PWM, interrupts, and LUT access. Bit masks encode DMA enable/update, display type, scan mode, interface width, pixel size, sync polarity, clocking, endianness, timing fields, and interrupt causes.

Control flow: board/platform code supplies pdata; the framebuffer driver programs DMA buffers, timing registers, pixel format, power/contrast, interrupts, and LUT entries using these constants during probe, mode set, blanking, and framebuffer updates.

State and persistence: runtime state lives in controller registers, DMA frame pointers, GPIO/backlight state, and framebuffer memory. Pdata is platform configuration rather than persistent kernel state.

Dependencies and integration points: depends on workqueue/list types and framebuffer monitor specs from surrounding includes. It integrates with Atmel platform devices, fbdev, board GPIO power control, DMA, and LCD panels.

Risks and test signals: risks include wrong bit masks/shifts, board wiring RGB/BGR mismatches, power sequencing via callbacks, DMA update races, and timing field limits. Test mode programming, blank/unblank, framebuffer pan/update, interrupt handling, RGB/BGR panels, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/aty128.h -->
# sources/distributed-fs/ceph-client/include/video/aty128.h

Purpose: provides ATI Rage128 framebuffer register offsets and bit constants for clocks, CRTC, DAC, GUI engine, blitter, PM4, LVDS, power management, and PCI/AGP control.

Important APIs and types: the header is macro-only. Register offsets cover MMIO control blocks including PLL, CRTC1/2, palette, memory, AGP/GART, PM4 command engine, overlay/capture, 2D/3D GUI registers, scissor, cache, and LVDS. Bit constants cover GUI idle/active, PLL write/reset/atomic update, pixel widths, DAC controls, soft resets, busy flags, data types, ROPs, drawing directions, LVDS/backlight enable, and power-management modes.

Control flow: the aty128 framebuffer driver uses these macros to initialize clocks, set display modes, program pitch/offset/palette, wait for engine idle, issue accelerated blits/fills, control LVDS panels, and handle power transitions.

State and persistence: live state is in Rage128 hardware registers, framebuffer memory, PLLs, and command FIFO/PM4 buffers. The header stores no software state.

Dependencies and integration points: integrates with the `aty128fb` driver, fbdev acceleration paths, PCI/AGP setup, panel/LVDS handling, and mode-setting code.

Risks and test signals: risks include wrong register offsets, duplicated `CRTC2_EN`, busy-wait deadlocks, PLL programming order, endian/pixel-format mismatch, and unsafe acceleration commands. Test mode set at multiple bpp, palette updates, acceleration operations, engine reset/idle waits, LVDS backlight, suspend/resume, and PCI/AGP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/aty128.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/broadsheetfb.h -->
# sources/distributed-fs/ceph-client/include/video/broadsheetfb.h

Purpose: defines Broadsheet e-paper framebuffer command/register constants and the board abstraction used by the broadsheet framebuffer driver.

Important APIs and types: command macros cover system/display init, register read/write, image load/load-area/end, wait triggers, waveform info, and full/update commands. Interface constants distinguish control pins and MMIO command/data writes. `broadsheetfb_par` holds fb info, board callbacks, register accessors, waitqueue, panel index, and IO lock. `broadsheet_board` supplies init/wait/cleanup/panel/IRQ plus GPIO or MMIO access callbacks.

Control flow: the driver initializes board hardware, writes controller registers/commands, loads image data, waits for display triggers/frame-end, and performs e-paper update sequences through board-specific GPIO/MMIO operations.

State and persistence: runtime state includes panel index, waitqueue events, IO lock, controller registers, and board-specific GPIO/MMIO state. Display contents may persist physically on e-paper but are not kernel-persistent data.

Dependencies and integration points: depends on fbdev, wait queues, mutexes, modules, and board glue. It integrates with platform-specific Broadsheet boards and framebuffer update paths.

Risks and test signals: risks include board callback lifetime, IO locking, wait-for-ready timeouts, panel type mismatch, and command ordering for e-paper updates. Test init/update/cleanup, IRQ wait paths, GPIO and MMIO boards, partial/full image loads, and timeout/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/broadsheetfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cirrus.h -->
# sources/distributed-fs/ceph-client/include/video/cirrus.h

Purpose: defines Cirrus Logic VGA/framebuffer chipset register indexes for sequencer, CRT controller, graphics controller, attribute controller, sleep, clock, cursor, and blitter extensions.

Important APIs and types: macro constants name POS/sleep ports, sequencer extension registers, CRT extension/status registers, graphics controller extension and BLT registers, and attribute controller extension registers for CL-GD542x/543x-style chips.

Control flow: the Cirrus framebuffer driver unlocks extension registers, programs clocks/timing/cursor, configures memory/performance, and drives the blitter using these register indexes.

State and persistence: live state is in VGA/Cirrus indexed registers and framebuffer memory. The header is macro-only.

Dependencies and integration points: integrates with `clgenfb`/Cirrus fbdev code and legacy VGA register access helpers.

Risks and test signals: risks include accessing scratch registers marked do-not-access, chipset revision differences, blitter register sequencing, and VGA index/data port races. Test mode set, cursor, acceleration, suspend/resume, and multiple CL-GD chip variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cirrus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cmdline.h -->
# sources/distributed-fs/ceph-client/include/video/cmdline.h

Purpose: declares helpers for retrieving parsed video command-line options for framebuffer/video drivers.

Important APIs and types: `video_get_options(name)` returns option text for a named video device. When `CONFIG_FB_CORE` is enabled, `__video_get_options(name, option, is_of)` is exported for fbdev compatibility.

Control flow: drivers call `video_get_options()` during probe or setup to fetch `video=` command-line configuration; fbdev compatibility code may call the internal helper with Open Firmware matching context.

State and persistence: parsed boot command-line options are global boot-time state maintained elsewhere. This header owns no state.

Dependencies and integration points: depends on kconfig and types. It integrates with fbdev core, boot parameter parsing, platform/of video drivers, and legacy mode option handling.

Risks and test signals: risks include option matching ambiguity, deprecated internal helper use, and behavior differences when `CONFIG_FB_CORE` is disabled. Test `video=` boot options for named devices, OF aliases, and configs with/without fbdev core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cmdline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cvisionppc.h -->
# sources/distributed-fs/ceph-client/include/video/cvisionppc.h

Purpose: defines Phase5 CyberVisionPPC/Permedia2 framebuffer board addresses, memory configuration constants, bridge flags, and private per-board state.

Important APIs and types: `cvppc_par` stores PCI config/bridge pointers and user flags. Macros define CyberStorm PPC bridge/config base addresses, ROM/register/framebuffer apertures, framebuffer size, old/new memory config values, memory clock, bridge endian bit, and active interrupt bit.

Control flow: the Permedia2 framebuffer driver maps board-specific PCI bridge/config/register/framebuffer apertures, configures endian/interrupt behavior, and uses memory constants during initialization.

State and persistence: runtime state is board MMIO mapping, user flags, bridge configuration, and framebuffer memory. The header contains platform constants only.

Dependencies and integration points: includes `pm2fb.h` and integrates with Amiga/PowerPC CyberVisionPPC hardware and the Permedia2 fbdev driver.

Risks and test signals: risks include hard-coded physical addresses, endian bridge handling, interrupt routing, and board revision memory config differences. Test probe/map on supported hardware, endian-correct rendering, interrupts, and old/new memory config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/cvisionppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/display_timing.h -->
# sources/distributed-fs/ceph-client/include/video/display_timing.h

Purpose: defines generic display timing data structures and flags for describing panel/display signal ranges before conversion to concrete video modes.

Important APIs and types: `enum display_flags` encodes hsync/vsync/data-enable polarity, pixel-data edge, interlace, doublescan, doubleclock, and sync edge. `timing_entry` stores min/typ/max values. `display_timing` groups pixel clock, horizontal/vertical active/porch/sync timings, and flags. `display_timings` holds an array of timings plus native mode. `display_timings_get()` safely retrieves an indexed timing, and `display_timings_release()` frees a collection.

Control flow: firmware/DT/panel parsers produce `display_timings`; drivers choose native or supported entries, convert timing ranges to `videomode`/DRM/fb modes, and release allocated timing arrays on teardown.

State and persistence: structures are runtime representations of persistent panel/firmware timing descriptions. The header does not own state.

Dependencies and integration points: depends on bitops and types. It integrates with OF display timing parsing, panel drivers, fbdev/DRM mode conversion, and `include/video/videomode.h`.

Risks and test signals: risks include invalid min/typ/max ordering, conflicting polarity flags, native index out of range, and memory ownership of timing arrays. Test DT timing parsing, multiple modes, native mode selection, invalid ranges, and release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/display_timing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/edid.h -->
# sources/distributed-fs/ceph-client/include/video/edid.h

Purpose: provides the kernel-side wrapper for the UAPI EDID block definition.

Important APIs and types: it includes `uapi/video/edid.h`, thereby exposing `struct edid_info` to kernel video code without defining additional symbols.

Control flow: kernel video/fbdev code includes this wrapper when it needs the legacy EDID UAPI container.

State and persistence: no state; all data is the raw EDID block passed through `edid_info`.

Dependencies and integration points: integrates UAPI EDID definitions into kernel include paths and legacy framebuffer display-probing code.

Risks and test signals: risks are include-path drift and assuming this wrapper provides EDID parsing helpers when it only exposes the raw container. Test compile coverage for video drivers including `video/edid.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/edid.h -->
