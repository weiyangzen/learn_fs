# subset-b-003729 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_combios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_combios.c

## Purpose

`radeon_combios.c` implements the legacy Radeon COMBIOS path for pre-AtomBIOS and selected compatibility configurations. It decodes legacy BIOS table offsets, constructs DDC/I2C records, derives clocks, panel data, DAC/TMDS parameters, connector topology, power states, and thermal-controller hints, runs legacy ASIC/PLL/MMIO initialization command tables, and updates BIOS scratch registers so firmware and driver agree on display ownership and attachment state.

This file is not a generic BIOS parser. It is a hardware-facing compatibility layer full of ASIC-family, board, and PowerMac-specific policy used by the Radeon KMS display and power-management setup paths when `rdev->is_atom_bios` is false or when older hardware needs COMBIOS-derived data.

## Important APIs, Types, and Functions

- `enum radeon_combios_table_offset`, `enum radeon_combios_ddc`, and `enum radeon_combios_connector` define the internal legacy table, DDC-line, and connector encodings used throughout the file.
- `combios_get_table_offset()` is the central table locator. It resolves absolute offsets from the BIOS header and relative offsets from other COMBIOS tables such as mobile info, misc info, memory config, and TMDS power tables.
- `radeon_combios_check_hardcoded_edid()` and `radeon_bios_get_hardcoded_edid()` validate and expose BIOS-provided EDID blocks for KVM/server or panel fallback.
- `combios_setup_i2c_bus()`, `radeon_combios_get_i2c_info_from_table()`, and `radeon_combios_i2c_init()` map legacy DDC identifiers and family-specific GPIO pads to `struct radeon_i2c_bus_rec` records and create Radeon I2C adapters.
- `radeon_combios_get_clock_info()` fills `rdev->clock` PLL limits, default SCLK/MCLK, and maximum pixel clock from the PLL info table.
- Display parameter helpers include `radeon_combios_get_primary_dac_info()`, `radeon_combios_get_tv_info()`, `radeon_combios_get_tv_dac_info()`, `radeon_combios_get_lvds_info()`, `radeon_legacy_get_tmds_info_from_combios()`, `radeon_legacy_get_tmds_info_from_table()`, `radeon_legacy_get_ext_tmds_info_from_combios()`, and `radeon_legacy_get_ext_tmds_info_from_table()`.
- Connector discovery entry points are `radeon_get_legacy_connector_info_from_table()` for built-in connector-table presets and `radeon_get_legacy_connector_info_from_bios()` for BIOS connector records. Both call `radeon_add_legacy_encoder()`, `radeon_add_legacy_connector()`, and `radeon_link_encoder_connector()`.
- `radeon_combios_get_power_modes()` creates basic power states, optional voltage GPIO data, PCIe lane hints, and I2C thermal-chip registrations from PowerPlay/Overdrive tables plus board-specific fallback quirks.
- `radeon_external_tmds_setup()` and `radeon_combios_external_tmds_setup()` program external TMDS/DVO chips either through fixed SIL164 writes or BIOS-scripted MMIO/PLL/I2C sequences.
- ASIC init helpers `combios_parse_mmio_table()`, `combios_parse_pll_table()`, `combios_parse_ram_reset_table()`, `combios_detect_ram()`, `combios_write_ram_size()`, and `radeon_combios_asic_init()` execute legacy initialization scripts and memory sizing.
- Scratch register helpers `radeon_combios_initialize_bios_scratch_regs()`, `radeon_combios_output_lock()`, `radeon_combios_connected_scratch_regs()`, `radeon_combios_encoder_crtc_scratch_regs()`, and `radeon_combios_encoder_dpms_scratch_regs()` maintain firmware-visible display state in Radeon BIOS scratch registers.

## Control Flow

Most consumers start by calling a narrow public helper rather than parsing the BIOS directly. Those helpers call `combios_get_table_offset()` to find a table, then use `RBIOS8/16/32` accessors to decode little-endian fields from `rdev->bios`. Clock and panel helpers populate persistent Radeon device or encoder-private structures; connector helpers build DRM encoders/connectors; init helpers write hardware registers.

The I2C flow first maps DDC identifiers to register addresses and bit masks in `combios_setup_i2c_bus()`. Family checks adjust ambiguous legacy lines such as `DDC_MONID` and `DDC_CRT2`; the resulting bus record is used by `radeon_i2c_create()`, `radeon_i2c_lookup()`, or `radeon_i2c_add()`. The special I2C info table path is used for system-specific GPIO pad masks.

Legacy connector discovery has two lanes. The table lane selects a platform connector table, including many PowerMac and embedded-board presets, then adds hardcoded combinations of encoders and connectors. The BIOS lane walks up to four packed connector entries, decodes connector type, DDC type, HPD bit, analog/digital device masks, dual-link information, and quirks, then adds LVDS and TV connectors from separate LCD/TV tables when present. Both lanes finish by linking encoders to connectors.

ASIC initialization is script-driven. `radeon_combios_asic_init()` runs ASIC init 1, PLL init, ASIC init 2, optional non-IGP memory scripts, RAM reset, ASIC init 3/4, memory-size detection/writes, and finally dynamic-clock table execution unless a board-specific RS4xx resume quirk skips it. The script interpreters decode compact command IDs and execute MMIO, PLL, read-modify-write, delay, and polling operations directly against hardware registers.

## State and Persistence Behavior

The file persists decoded results in shared driver state: `rdev->i2c_bus[]`, `rdev->clock`, `rdev->mode_info.bios_hardcoded_edid`, `rdev->mode_info.connector_table`, encoder private structures, `rdev->pm.power_state`, `rdev->pm.i2c_bus`, and BIOS scratch registers. Connector and encoder objects created by the discovery paths become part of DRM mode configuration and outlive the parser call.

Hardware writes are persistent until later modesetting, reset, suspend/resume, or firmware interaction changes them. The ASIC init and TMDS setup paths write MMIO, PLL, memory-size, memory-controller, and I2C device registers. Scratch register helpers persist display status bits that are used by BIOS/ACPI paths and by other Radeon display code.

Allocation ownership is split. This file allocates DAC/LVDS/TMDS/power-state data with Radeon allocation helpers and stores the resulting pointers in caller-owned encoder or device state. It validates hardcoded EDID into `rdev->mode_info.bios_hardcoded_edid`, while callers receive duplicates through `radeon_bios_get_hardcoded_edid()`.

## Dependencies and Integration Points

- DRM/KMS: `struct drm_device`, connector/encoder types, EDID validation/duplication, display mode structures, and logging.
- Radeon core headers and register macros: `radeon.h`, `radeon_legacy_encoders.h`, `radeon_reg.h` via included headers, `RREG*`, `WREG*`, `RBIOS*`, ASIC family predicates, and device flags.
- Atom definitions: connector object IDs, device support masks, encoder enums, and TV/panel constants from `atom.h` and related AtomBIOS headers are reused even in COMBIOS paths.
- I2C and thermal integration: `radeon_i2c_create()`, `radeon_i2c_lookup()`, `radeon_i2c_put_byte()`, and `i2c_new_client_device()` connect BIOS-derived buses and thermal chips to kernel I2C.
- Power/display integration: Radeon mode setup consumes the connector and encoder topology, power management consumes `rdev->pm.power_state`, and encoder paths call TMDS/DAC/LVDS helpers for private data.
- Platform integration: `CONFIG_PPC_PMAC` and `CONFIG_PPC64` branches select Apple and RN50 connector tables from Open Firmware or ASIC predicates.

## Risks and Edge Cases

- BIOS bounds are mostly trusted. Many offset walks and table interpreters advance through firmware data until sentinel values without validating against the actual ROM length.
- Board-specific quirks are numerous and fragile. Incorrect PCI ID matching or missing a new quirk can create phantom connectors, broken resume, wrong DDC routing, or bad DAC calibration.
- The legacy table offset function mixes absolute and relative table lookup rules; malformed revisions or bad intermediate offsets can redirect later parsing.
- Connector discovery may add fallback VGA/DVI/LVDS/TV outputs from partial tables. That improves old-board support but risks exposing nonexistent connectors when firmware is wrong.
- ASIC init scripts directly write MMIO/PLL/memory registers and include busy-wait loops. Bad table data or unsupported hardware can hang, delay, or misprogram display/memory state.
- `combios_detect_ram()` writes and reads aperture addresses during memory sizing on old non-IGP ASICs; this is inherently risky if memory controller setup is not already sane.
- Power-mode allocation has a `pm_failed` path that leaves partially allocated subobjects for broader cleanup code to handle; lifecycle changes should verify no leaks or double frees.
- External TMDS setup depends on I2C bus discovery and firmware script correctness; wrong slave addresses or unrecognized script IDs silently limit display bring-up.

## Test Signals

- BIOS parser tests should cover missing BIOS, invalid/missing table offsets, multiple table revisions, sentinel-terminated MMIO/PLL/RAM reset scripts, and hardcoded EDID validation/failure.
- Connector tests should exercise generic, mobility, IGP, PowerMac, RN50, DVI-I/DVI-D, LVDS, TV, shared DDC, dual-link, and known PCI-ID quirk paths.
- I2C tests should verify DDC identifier mapping by ASIC family, GPIOPAD/MDGPIO masks, system-specific I2C table overrides, and hardware-capability flags.
- Hardware or simulator tests should confirm legacy ASIC init writes expected register sequences and that RS4xx resume quirks skip the dynamic-clock table.
- Power-management tests should validate PowerPlay-derived battery/default states, voltage GPIO fields, thermal I2C registration, missing-table fallbacks, and default clock propagation.
- Runtime signals include correct mode enumeration on old Radeon boards, no phantom TV/VGA connectors on known-quirk systems, stable suspend/resume on RS4xx systems, and BIOS scratch bits matching connector/DPMS/CRTC changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_combios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_connectors.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_connectors.c

## Purpose

`radeon_connectors.c` implements Radeon DRM connector behavior for VGA, DVI/HDMI, DisplayPort/eDP/LVDS, TV, DP bridges, and legacy connectors. It owns connector initialization, detect callbacks, mode enumeration, mode validation, property handling, EDID retrieval, HPD handling, scratch-register updates, and connector destruction for both AtomBIOS and legacy COMBIOS topology paths.

The file is the main bridge between firmware-discovered connector topology and Linux DRM connector semantics. It decides whether a connector is connected, which encoder should drive it, which modes are exposed, and which user-visible properties trigger a modeset.

## Important APIs, Types, and Functions

- `radeon_connector_hotplug()` handles HPD events, polarity updates, and DisplayPort retraining when an already-enabled DP sink needs link training after plug changes.
- `radeon_get_monitor_bpc()` calculates the effective bits-per-channel from EDID/display info, connector type, ASIC generation, HDMI deep-color limits, max TMDS clock, and the `radeon_deep_color` module parameter.
- EDID helpers `radeon_connector_get_edid()`, `radeon_connector_free_edid()`, and `radeon_ddc_get_modes()` retrieve EDID over AUX, DDC, switcheroo DDC, or BIOS fallback and publish modes/properties.
- Encoder/mode helpers include `radeon_find_encoder()`, `radeon_best_single_encoder()`, `radeon_get_native_mode()`, `radeon_fp_native_mode()`, `radeon_add_common_modes()`, and `radeon_connector_analog_encoder_conflict_solve()`.
- Property handling is centralized in `radeon_connector_set_property()` for coherent mode, audio, dithering, underscan, TV standard, DAC load detect, TMDS PLL source, scaling mode, and output CSC. `radeon_lvds_set_property()` provides a smaller LVDS/eDP scaling path.
- Connector families have specific callbacks: LVDS (`radeon_lvds_get_modes()`, `radeon_lvds_mode_valid()`, `radeon_lvds_detect()`), VGA (`radeon_vga_get_modes()`, `radeon_vga_mode_valid()`, `radeon_vga_detect()`), TV (`radeon_tv_get_modes()`, `radeon_tv_mode_valid()`, `radeon_tv_detect()`), DVI/HDMI (`radeon_dvi_detect()`, `radeon_dvi_encoder()`, `radeon_dvi_force()`, `radeon_dvi_mode_valid()`), and DP/eDP (`radeon_dp_get_modes()`, `radeon_dp_detect()`, `radeon_dp_mode_valid()`).
- DisplayPort support helpers include `radeon_connector_encoder_get_dp_bridge_encoder_id()`, `radeon_connector_encoder_is_hbr2()`, `radeon_connector_is_dp12_capable()`, `radeon_connector_late_register()`, and AUX unregister/register paths.
- Public connector constructors `radeon_add_atom_connector()` and `radeon_add_legacy_connector()` allocate `struct radeon_connector`, attach DDC/AUX/router data, initialize DRM connector funcs/helpers, set properties, polling flags, subpixel order, and register the connector.

## Control Flow

Connector creation is driven by firmware parsing elsewhere. `radeon_add_atom_connector()` handles AtomBIOS-era connectors and DP bridges, while `radeon_add_legacy_connector()` handles COMBIOS-era outputs. Both avoid unknown connectors and optional TV outputs disabled by `radeon_tv`, merge duplicate connector IDs by OR-ing device masks, look up DDC buses, initialize the correct DRM connector function table, attach mode properties, set polling policy, set subpixel order, and register the connector. Atom connectors additionally allocate `struct radeon_connector_atom_dig` for digital outputs and initialize AUX for DP-capable DDC buses.

Detection callbacks first acquire runtime PM unless already running as the KMS poll worker. LVDS/eDP checks native panel validity and EDID/DPCD. VGA probes DDC first, then optionally load-detects DACs on forced probes. DVI/HDMI performs DDC probing, analog-vs-digital EDID interpretation, shared-DDC filtering, HPD-without-DDC retry scheduling, optional DAC load detection, and audio detection. DP detects eDP panels, DP bridges, native DP sinks, and passive adapters through a mixture of HPD, DPCD, AUX, and DDC probing.

Mode enumeration follows detection state. EDID modes are preferred when available. Panel connectors repair or synthesize native modes from EDID, VBIOS-provided native mode, or CVT approximation, then add scaled common modes. TV connectors expose either common scaled modes on newer ASICs or an 800x600 fallback on older hardware. Mode-validation callbacks apply panel bounds, scaling policy, TMDS clock limits, HDMI 1.3 limits on DCE6, RV100 heat-related DVI limits, max pixel clock, and DP bandwidth helper results.

Property changes mutate connector or encoder private state and then call `radeon_property_change_mode()` to reapply the active CRTC mode when necessary. Output CSC changes may update the CRTC CSC and invoke gamma programming immediately.

## State and Persistence Behavior

Each `struct radeon_connector` persists EDID cache, DDC bus, AUX presence, HPD record, router data, supported device mask, connector object ID, shared-DDC status, load-detect flag, detected-by-load state, digital/analog selection, audio/dither properties, and digital connector private data. EDID is cached between get-modes and detect operations until explicitly freed during detection or destruction.

Connector status changes are mirrored into BIOS scratch registers through `radeon_connector_update_scratch_regs()`, which dispatches to AtomBIOS or COMBIOS scratch helpers for every possible encoder. This keeps firmware-facing attachment state synchronized with DRM connector state and selected best encoder.

Runtime PM references are transient around detect paths. AUX registration state persists after late registration and is undone in early unregister/destroy. User-visible properties persist in connector/encoder private fields and are applied on subsequent modesets.

## Dependencies and Integration Points

- DRM core and helpers: connector/encoder init, mode probing, EDID, DP MST/AUX helpers, helper DPMS, property APIs, runtime connector registration, and CRTC helper modesets.
- Radeon display stack: `radeon.h`, `radeon_audio.h`, `atom.h`, encoder private structs, DP helpers, DDC/I2C helpers, router selection, HPD sense/polarity, Atom/COMBIOS scratch updates, and external encoder DDC setup.
- Power management: `pm_runtime_get_sync()`, `pm_runtime_put_autosuspend()`, KMS poll-worker checks, and switcheroo DDC support.
- Module/config policy: `radeon_audio`, `radeon_deep_color`, `radeon_tv`, `radeon_runtime_pm`, ASIC family macros, and device flags control behavior.
- Firmware integration: hardcoded EDID fallback, Atom panel power actions for eDP, DP bridge IDs, encoder capability records, and native panel modes from encoder setup.

## Risks and Edge Cases

- Hotplug and DPMS state are not fully locked; `radeon_connector_hotplug()` explicitly notes unprotected `connector->dpms` access.
- Detection is intentionally conservative in some paths and destructive in others. DAC load detection is avoided unless forced for VGA/DVI, but still can perturb analog outputs.
- Shared DDC handling is heuristic, especially for VGA+HDMI and DVI-D+HDMI board layouts. Misclassification can hide a real connector or expose the wrong one.
- HPD without DDC schedules a delayed retry for DVI. This reduces false negatives but introduces timing-sensitive state in `detected_hpd_without_ddc`.
- BIOS EDID fallback can mark disconnected server/KVM outputs connected when normal probing fails, which is useful but may create permanent virtual outputs.
- Several property paths assume `best_encoder()` returns a valid encoder when no current encoder is set. Unexpected topology gaps could lead to null dereferences if firmware created incomplete connector links.
- `radeon_connector_late_register()` dereferences `radeon_connector->ddc_bus` before checking `has_aux`; callers must only use it for connector types that were initialized with a DDC bus.
- Deep-color BPC calculation depends on `pixelclock_for_modeset` being set before modeset validation; stale or zero clocks can degrade or misreport BPC.

## Test Signals

- Connector construction tests should verify property attachment, polling flags, DDC/AUX assignment, duplicate connector merging, router exceptions to shared DDC, and DP bridge handling.
- Detection tests should cover DDC success/failure, invalid EDID, null EDID RS690/RS740 behavior, HPD-only DVI retry, DAC load detect, shared DDC analog/digital filtering, BIOS EDID fallback, and runtime-PM error paths.
- DP/eDP tests should exercise DPCD retrieval, panel power sequencing, passive DP adapters, DP bridge DDC setup, AUX registration/unregistration, DP 1.2 capability gating, and link retraining on hotplug.
- Mode tests should validate panel native mode repair, common scaled modes, TV fallback modes, DVI/HDMI clock limits, max pixel clock limits, deep-color degradation by max TMDS clock, and DP bandwidth validation.
- Property tests should assert that changing audio/dither/underscan/coherent/scaling/output-CSC/TV-standard state triggers the expected modeset or gamma update without changing unrelated connectors.
- Runtime signals include stable hotplug behavior, correct audio detection for digital outputs, no lockdep/runtime-PM warnings during polling, and accurate BIOS scratch updates after connector status changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_connectors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cs.c

## Purpose

`radeon_cs.c` implements Radeon command-submission parsing and submission for DRM userspace. It copies and validates command-stream chunks, resolves GEM relocation handles, validates and reserves buffer objects, allocates indirect buffers, synchronizes reservations across rings, schedules IBs on legacy or VM rings, updates VM page tables for VM submissions, handles GPU reset retry signaling, and provides packet/relocation parsing helpers used by ASIC-specific command-stream validators.

This file is on a security-sensitive ioctl path: it translates untrusted userspace command submission into validated GPU work and must constrain memory domains, ring selection, relocation references, packet bounds, fences, and VM mappings.

## Important APIs, Types, and Functions

- `struct radeon_cs_buckets` and helpers `radeon_cs_buckets_init()`, `radeon_cs_buckets_add()`, and `radeon_cs_buckets_get_list()` implement stable priority bucketing for relocation validation ordering.
- `radeon_cs_parser_init()` copies userspace chunk descriptors and chunk data, identifies IB/CONST_IB/RELOCS/FLAGS chunks, sets command-submission flags, ring ID, priority, and validates ring/parser compatibility.
- `radeon_cs_get_ring()` maps UAPI ring IDs and priority to internal ring indices for GFX, compute, DMA, UVD, and VCE.
- `radeon_cs_parser_relocs()` looks up GEM BO handles, assigns preferred/allowed domains, handles UVD/AGP/IGP VRAM requirements, rejects CPU domains, constrains userptr and dma-buf shared BOs, optionally collects VM BOs, and calls `radeon_bo_list_validate()`.
- `radeon_cs_sync_rings()` imports reservation fences from validated BOs into the IB sync object.
- `radeon_cs_parser_fini()` adds the scheduled IB fence to BO reservations on success, sorts BOs by size for LRU behavior, releases parser allocations, GEM references, VM BO arrays, and IBs.
- `radeon_cs_ib_fill()` allocates IB and optional const IB memory, enforces VM IB size limits, and copies command dwords from userspace or pre-copied AGP data.
- `radeon_cs_ib_chunk()` handles non-VM command streams: ASIC parser validation, ring synchronization, UVD/VCE usage notification, and IB scheduling.
- `radeon_cs_ib_vm_chunk()` handles VM command streams: optional const-IB parse, IB parse, VM mutex locking, page-table updates, sync, and IB scheduling.
- `radeon_bo_vm_update_pte()` updates the VM page directory, clears freed/invalid mappings, updates the temporary IB BO and all relocation BO mappings, syncs page-table update fences, and reserves BO fence slots.
- `radeon_cs_ioctl()` is the DRM ioctl entry point coordinating exclusive-lock checks, reset handling, parser init, IB fill, relocation validation, tracing, submission, cleanup, and lockup retry conversion.
- Packet helpers `radeon_cs_packet_parse()`, `radeon_cs_packet_next_is_pkt3_nop()`, `radeon_cs_dump_packet()`, and `radeon_cs_packet_next_reloc()` are exported to ASIC-specific CS parsers.

## Control Flow

`radeon_cs_ioctl()` takes `rdev->exclusive_lock` for read, rejects submissions when acceleration is down, and handles an in-progress reset by attempting `radeon_gpu_reset()` and returning `-EAGAIN` on success. It initializes a zeroed parser, calls `radeon_cs_parser_init()`, fills the IB with `radeon_cs_ib_fill()`, parses and validates relocations, emits a tracepoint, submits either non-VM or VM IB chunks, finalizes parser state, releases the exclusive lock, and maps `-EDEADLK` lockup results through `radeon_cs_handle_lockup()`.

Parser initialization copies a userspace array of chunk pointers, then copies each chunk descriptor. Relocation and flags chunks are copied immediately. Normal IB chunks are not copied unless AGP requires pre-copying, because they are later copied into the allocated IB. CONST_IB data is copied into a separate const IB for supported VM submissions. The flags chunk can select VM mode, ring, and priority.

Relocation parsing treats each relocation as four dwords. It looks up the GEM object, records the Radeon BO, computes priority from userspace priority plus write-domain status, and assigns domains. UVD first buffers and legacy AGP/IGP paths are forced to VRAM. Userptr BOs are forced to GTT and require taking `mmap_read_lock()` during validation. dma-buf shared BOs are prevented from moving into VRAM. The bucketed relocation list is validated as an execution list, and VM submissions additionally append VM BOs.

Submission splits by VM flag. Non-VM submissions call the ring-specific CS parser before scheduling. VM submissions call ring IB parsers for const and regular IBs, update VM page tables under `vm->mutex`, synchronize reservation fences, and schedule both IBs on SI+ when const IB is present.

Packet parsing helpers operate on `p->chunk_ib` and `radeon_get_ib_value()`. They validate packet type, count, and bounds, dump the IB on malformed packets, recognize PKT3 NOP relocation packets, and translate relocation packet indices into `p->relocs` entries.

## State and Persistence Behavior

Most parser state is per-ioctl and released in `radeon_cs_parser_fini()`: copied chunks, relocation arrays, VM BO arrays, tracker state, IBs, and GEM references. Successful submissions persist fences into each BO reservation object so future CPU/GPU users synchronize with the submitted IB.

Validated BO placement and VM page-table updates persist beyond the ioctl. `radeon_bo_list_validate()` may move BOs between domains. `radeon_bo_vm_update_pte()` updates VM mappings and page-directory state for the file-private VM. UVD/VCE usage notifications persist into power-management/video-block usage tracking.

The parser records `cs_flags`, selected ring, priority, relocation sharing, and IB sync state for the duration of submission. `radeon_cs_parser_fini()` always frees IB allocations, even on errors, but only attaches the IB fence to BO reservations when `error` is zero.

## Dependencies and Integration Points

- DRM/GEM/TTM: GEM lookup and put, dma reservation fences, `drm_exec`, BO validation, userptr checks, dma-buf sharing, and reservation synchronization.
- Kernel userspace access: `copy_from_user()`, `kvmalloc_array()`, `kvzalloc_objs()`, `mmap_read_lock()`, and `mmap_read_unlock()`.
- Radeon subsystems: ring definitions and parsers, IB allocation/scheduling/free, VM manager, VM BO update routines, BO lists, sync helpers, GPU reset, UVD/VCE usage tracking, and tracepoints.
- UAPI: `struct drm_radeon_cs`, `struct drm_radeon_cs_chunk`, `struct drm_radeon_cs_reloc`, `RADEON_CHUNK_ID_*`, `RADEON_CS_*`, relocation domains, and packet encodings from `radeon_drm.h` and register headers.
- ASIC-specific parsers call packet and relocation helpers to validate command streams against per-family register and packet rules.

## Risks and Edge Cases

- The ioctl consumes untrusted chunk pointers and lengths. Integer overflow in length calculations is partly mitigated by `kvmalloc_array()`, but every later size and index calculation remains security relevant.
- Relocation parsing assumes four dwords per relocation. Malformed relocation chunks with non-multiple lengths can produce truncated logical entries or unused trailing data.
- Error paths in parser initialization return before all chunks are processed; cleanup relies on zero-initialized parser fields and `radeon_cs_parser_fini()` handling partial state.
- The bucket sorting helper uses list splicing in ascending bucket index despite comments about descending priority. Because `list_splice()` inserts each bucket at the head of `out_list`, final order may still be high-priority first, but this behavior is subtle and regression-prone.
- `radeon_cs_get_ring()` silently maps unsupported compute on pre-Tahiti to GFX and chooses low/high priority DMA/compute rings by sign of priority; changes to ring policy can affect scheduling fairness and compatibility.
- `radeon_cs_packet_next_reloc()` validates `idx >= length_dw` but then assumes `idx + 3` exists in nomm mode and `idx / 4` indexes `p->relocs`; malformed NOP relocation packets can stress parser assumptions if an ASIC parser calls it without earlier validation.
- VM submissions require the BO to already exist in the file-private VM; missing mappings are hard errors. Page-table update fence reservation failures must unwind without leaving inconsistent sync state.
- `-EDEADLK` is converted into GPU reset and `-EAGAIN`, so callers must be prepared to resubmit.

## Test Signals

- UAPI tests should cover zero chunks, missing IB, zero-length IB/CONST_IB/FLAGS, bad chunk pointers, invalid copy lengths, bad ring IDs, unsupported VM flags, and priority ring selection.
- Relocation tests should cover missing handles, CPU domain rejection, VRAM/GTT fallback for VRAM-only domains, UVD first-buffer VRAM forcing, AGP/IGP behavior, userptr GTT enforcement with mmap lock, and dma-buf VRAM exclusion.
- Submission tests should exercise non-VM parser failure, VM parser failure, const IB scheduling on SI+, sync failures, VM page-table update failures, UVD/VCE usage notes, fence attachment on success, and no fence attachment on error.
- Packet helper tests should validate type0/type2/type3 parsing, unknown packet dumps, count bounds, PKT3 NOP detection, relocation packet index mapping, and malformed relocation packet handling.
- Locking/reset tests should cover exclusive-lock behavior, `accel_working` false, `in_reset`, `-EDEADLK` reset conversion, `-ERESTARTSYS` logging suppression, VM mutex coverage, and reservation fence slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cursor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cursor.c

## Purpose

`radeon_cursor.c` implements hardware cursor programming for Radeon CRTCs. It supports legacy, AVIVO, and DCE4+ cursor register layouts; pins user-provided GEM cursor images into VRAM; updates cursor dimensions, hot spots, addresses, and positions; hides cursors when they move outside the visible CRTC area; and restores cursor state after modeset/reset events.

This file is a small but hardware-sensitive part of the KMS CRTC API. It translates DRM cursor set/move calls into register writes while respecting ASIC-specific cursor limits and legacy address restrictions.

## Important APIs, Types, and Functions

- `radeon_lock_cursor()` toggles the cursor update-lock bit for DCE4, AVIVO, or legacy cursor registers so multi-register cursor updates can be applied atomically enough for the hardware.
- `radeon_hide_cursor()` disables cursor display or clears enable bits using the appropriate register family.
- `radeon_show_cursor()` writes the pinned cursor surface address and enables the hardware cursor in the ASIC-specific format.
- `radeon_cursor_move_locked()` updates cached cursor coordinates, applies CRTC offsets and hot-spot origins, handles AVIVO pre-DCE6 boundary workarounds, writes position/hot-spot/size registers, and hides/shows based on out-of-bounds state.
- `radeon_crtc_cursor_move()` is the DRM cursor move hook wrapper that locks updates around `radeon_cursor_move_locked()`.
- `radeon_crtc_cursor_set2()` is the DRM cursor set hook. It disables the cursor for handle zero, validates dimensions, looks up the GEM object, reserves and pins the Radeon BO in VRAM, updates cursor geometry and hot spot, shows the new cursor, unpins and releases the old cursor BO, and stores the new object.
- `radeon_cursor_reset()` reprograms the current cursor image and position after CRTC state has been reset or modes have been restored.

## Control Flow

Cursor movement enters through `radeon_crtc_cursor_move()`, which locks cursor updates, calls the locked movement helper, and unlocks. The helper caches the logical cursor x/y, translates coordinates differently for AVIVO and legacy hardware, computes hot-spot origins for negative x/y, applies AVIVO multi-CRTC boundary restrictions before DCE6, tests the cursor against the CRTC visible rectangle, and either writes registers or hides the cursor and marks it out of bounds.

Cursor image changes enter through `radeon_crtc_cursor_set2()`. A zero handle hides the cursor and jumps to old-BO unpin. Nonzero handles are dimension-checked, looked up as GEM objects, converted to Radeon BOs, reserved, and pinned into VRAM. Legacy cursor hardware is restricted to a 27-bit offset, while AVIVO/DCE paths pass no upper restriction. After pinning, the function locks cursor updates, adjusts cached cursor position if width/height/hot spot changed, updates dimensions and hot spot, calls `radeon_show_cursor()`, unlocks, then unpins and drops the previous cursor object.

Reset flow is simple: if a cursor BO is still assigned, `radeon_cursor_reset()` locks cursor updates, rewrites position and visibility through `radeon_cursor_move_locked()` and `radeon_show_cursor()`, then unlocks.

## State and Persistence Behavior

Per-CRTC cursor state persists in `struct radeon_crtc`: `cursor_x`, `cursor_y`, `cursor_width`, `cursor_height`, `cursor_hot_x`, `cursor_hot_y`, `cursor_addr`, `cursor_bo`, `cursor_out_of_bounds`, `max_cursor_width`, `max_cursor_height`, `crtc_offset`, `crtc_id`, and `legacy_display_base_addr`. This cached state lets moves, set-image calls, and resets interact without rereading hardware.

The cursor BO remains pinned in VRAM while assigned to the CRTC and is unpinned when replaced or disabled. Register writes persist until another cursor update, modeset, reset, or CRTC disable changes them. `cursor_out_of_bounds` prevents repeated hide writes and gates re-show when a cursor comes back into bounds.

## Dependencies and Integration Points

- DRM CRTC cursor hooks call `radeon_crtc_cursor_move()` and `radeon_crtc_cursor_set2()`.
- GEM/TTM/Radeon BO APIs provide object lookup, reference release, reserve/unreserve, pin restricted, and unpin operations.
- Radeon register macros and ASIC predicates select DCE4, AVIVO, RV770+, and legacy register programming.
- CRTC mode state (`crtc->x`, `crtc->y`, `crtc->mode`, `crtc->enabled`) is used for coordinate translation and AVIVO boundary workarounds.
- Legacy display-base state from the CRTC is required because old cursor offsets are relative to `DISP(2)_BASE_ADDRESS`.

## Risks and Edge Cases

- Cursor updates rely on register-level locks, not a broader modeset lock in this file. Callers must provide the normal DRM/KMS serialization.
- The old cursor BO is unpinned after the new cursor is shown. If unpin reserve fails, the code still drops the GEM reference, relying on BO lifetime and later cleanup to tolerate the pinned state.
- Legacy cursor address restriction is enforced at pin time with `1 << 27`; incorrect domain placement or large VRAM layouts can reject otherwise valid cursor images on old ASICs.
- AVIVO pre-DCE6 has a special 128-pixel boundary and dual-CRTC workaround that shrinks effective cursor width. Off-by-one mistakes here can make cursors disappear near right edges.
- Negative-coordinate handling caps origin at `max_cursor_width - 1`/`max_cursor_height - 1`; unusual cursor sizes or max values can affect partially visible cursors.
- `radeon_show_cursor()` returns early when `cursor_out_of_bounds` is set, so callers must clear that state through movement before expecting the cursor to reappear.
- Width and height are validated against maximums but not explicitly against zero in this file. DRM callers usually avoid zero-size cursors, but direct misuse would program `w - 1` or `height - 1` values.

## Test Signals

- Cursor set tests should cover disable via handle zero, invalid dimensions, missing GEM handles, reserve/pin failures, successful pin/show, old BO unpin/release, and hot-spot-induced position adjustment.
- Move tests should cover in-bounds, fully out-of-bounds, partially negative x/y, CRTC offsets, doublescan legacy y scaling, and re-entry from out-of-bounds.
- ASIC tests should validate register writes for DCE4+, AVIVO/RV770 high-address programming, and legacy cursor offset/enable paths.
- Boundary tests should exercise AVIVO pre-DCE6 dual-CRTC right-edge and 128-pixel-boundary cases, plus DCE6+ behavior where the workaround is skipped.
- Reset tests should verify that an assigned cursor is reprogrammed after modeset/reset and that no writes occur when `cursor_bo` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cursor.c -->
