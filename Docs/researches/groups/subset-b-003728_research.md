# subset-b-003728

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.c

Purpose: implements the Radeon AtomBIOS interpreter-facing discovery and control layer. It converts ATOM firmware data tables into DRM connectors, encoders, GPIO/I2C buses, HPD pins, PLL limits, panel and TV modes, spread-spectrum settings, power states, voltage tables, VRAM timing metadata, memory-controller register tables, and BIOS scratch-register state.

Important APIs/functions: `radeon_atombios_i2c_init` creates `rdev->i2c_bus[]` entries from `GPIO_I2C_Info`; `radeon_atombios_lookup_gpio` and `radeon_atom_get_hpd_info_from_gpio` map ATOM GPIO IDs to Radeon GPIO/HPD records; `radeon_get_atom_connector_info_from_object_table` parses the ATOM object/path tables for modern connector discovery; `radeon_get_atom_connector_info_from_supported_devices_table` handles older `SupportedDevicesInfo`; `radeon_atom_get_clock_info` fills `rdev->clock` PLL/default-clock fields; `radeon_atombios_get_power_modes` builds `rdev->pm.power_state`; `radeon_atom_get_clock_dividers`, `radeon_atom_get_memory_pll_dividers`, `radeon_atom_set_engine_clock`, `radeon_atom_set_memory_clock`, and voltage helpers call ATOM command tables. Other public helpers expose TMDS, spread spectrum, LVDS, TV, DAC, VRAM, MC register, and scratch-register data.

Control flow: connector discovery first parses ATOM data headers through `atom_parse_data_header`, walks object or supported-device records, applies board-specific quirks, looks up DDC/HPD/router records, adds encoders/connectors through Radeon mode helpers, and finally links encoders to connectors. Clock and voltage control code switches on ATOM table firmware/content revisions and ASIC family to choose the right packed table layout or command argument structure. PowerPlay parsing similarly dispatches between legacy table revisions 1-3 and PPLIB revisions 4-6, allocates per-state clock arrays, filters invalid zero-clock modes, and assigns default/current PM indices.

State and persistence: most work mutates in-memory device state under `struct radeon_device`: `mode_info`, `clock`, `pm`, `i2c_bus`, BIOS hardcoded EDID, and saved scratch registers. It can register external I2C thermal clients via `i2c_new_client_device`. Scratch helpers persist display status into GPU BIOS scratch registers across mode operations and save/restore those registers around suspend/resume style transitions. There is no filesystem persistence.

Dependencies and integration: depends on ATOM parser APIs from `atom.h`/`atom-bits.h`, DRM connector/mode/EDID types, Radeon ASIC/register helpers, mode helpers such as `radeon_add_atom_connector`, `radeon_add_atom_encoder`, `radeon_link_encoder_connector`, `radeon_i2c_create`, and low-level register macros. PM/DPM, display, backlight, I2C, thermal, and suspend/resume paths consume the populated state.

Risks: firmware tables are trusted heavily and parsed with many pointer casts, revision-dependent structure sizes, and variable-length records, so malformed BIOS data can cause invalid offsets or incomplete state. Board quirks are PCI-ID-specific and easy to regress. Power table parsing allocates nested clock arrays and must avoid leaks on invalid modes. Clock/voltage ATOM command execution directly affects hardware stability. Scratch-register updates must preserve unrelated firmware bits. Several paths silently fall back or return false, so missing data can degrade display or PM behavior without an explicit hard failure.

Test signals: boot and modeset testing on ATOM and legacy Radeon ASICs; connector enumeration, DDC, HPD, LVDS/eDP panel, TV, and multi-output tests; suspend/resume scratch-register checks; dynamic PM/DPM clock and voltage transition tests; fault-injection or synthetic VBIOS table tests for revision/size handling; kernel logs containing `DRM_ERROR`, `DRM_INFO`, and connector/clock discovery output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.h

Purpose: declares the small private AtomBIOS display-facing interface shared by Radeon driver compilation units.

Important APIs/types/functions: forward-declares `drm_connector`, `drm_device`, `drm_display_mode`, `radeon_device`, and `radeon_encoder`. Exposes `radeon_atom_get_tv_timings` for analog TV mode timing extraction, `radeon_add_atom_encoder` for creating AtomBIOS-backed encoders, and `radeon_atom_backlight_init` for AtomBIOS panel backlight setup.

Control flow: this header has no runtime control flow. It defines compile-time linkage between AtomBIOS implementation code and callers in the Radeon display stack.

State and persistence: no state is stored here. The declared functions operate on runtime DRM/Radeon objects supplied by callers.

Dependencies and integration: guarded by `__RADEON_ATOMBIOS_H__`. Included by AtomBIOS and display encoder/backlight code that needs the private prototypes without importing full struct definitions.

Risks: prototype drift against implementation or caller expectations would break builds or produce ABI mismatches inside the kernel module. Because the declarations use forward types, callers still need the right full definitions before dereferencing objects.

Test signals: normal Radeon kernel build coverage, especially compilation units that include this header and call TV timing, encoder creation, or backlight initialization helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atombios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atpx_handler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atpx_handler.c

Purpose: implements ACPI ATPX support for hybrid Intel/ATI or integrated/discrete Radeon switchable graphics systems and registers Radeon callbacks with `vga_switcheroo`.

Important APIs/functions/types: public queries `radeon_has_atpx`, `radeon_has_atpx_dgpu_power_cntl`, `radeon_is_atpx_hybrid`, and `radeon_atpx_dgpu_req_power_for_displays` expose detected capability state. `radeon_register_atpx_handler` and `radeon_unregister_atpx_handler` manage switcheroo registration. Internal types model ATPX function masks and ACPI buffers: `radeon_atpx_functions`, `radeon_atpx`, `atpx_verify_interface`, `atpx_px_params`, `atpx_power_control`, and `atpx_mux`. Core helpers include `radeon_atpx_call`, `radeon_atpx_verify_interface`, `radeon_atpx_validate`, mux switch helpers, and `radeon_atpx_set_discrete_state`.

Control flow: registration calls `radeon_atpx_detect`, which scans PCI VGA and display-other devices, looks for an ACPI `ATPX` handle, counts GPUs, records bridge D3 support, and initializes ATPX only on two-GPU systems. Initialization verifies the ACPI interface, parses function bits, reads PX parameters when available, derives required mux/power-control behavior, and marks Microsoft hybrid graphics. `vga_switcheroo` callbacks then translate client IDs into ATPX integrated/discrete mux values, call switch-start, display mux, I2C mux, switch-end in order, or call power control for the discrete GPU.

State and persistence: all persistent state is process-lifetime kernel memory in the static `radeon_atpx_priv`: detection flag, bridge power-management usability, ACPI device handle, ATPX handle, supported function booleans, and hybrid flags. ACPI calls may change platform firmware state, display mux state, and discrete GPU power state. There is no filesystem persistence.

Dependencies and integration: depends on Linux ACPI, PCI enumeration, `vga_switcheroo`, bridge D3 metadata, and Radeon ATPX constants from `radeon_acpi.h`. The handler integrates Radeon GPUs with generic Linux switchable graphics policy and platform firmware.

Risks: ACPI method buffers are firmware-provided and only minimally size-checked before casts. Device enumeration assumes exactly two relevant display devices for ATPX registration. Power control is disabled for some hybrid systems when bridge D3 is usable, so platform-specific PM behavior can diverge. Switch and power callbacks ignore several helper return values, making partial ACPI failures hard to surface. A fixed 200 ms delay after power-off is required and may be platform-sensitive.

Test signals: hybrid laptop boot logs showing detected ATPX method and version/function bits; `vga_switcheroo` switch and power-cycle tests; suspend/resume and runtime PM tests on muxed and muxless hybrid platforms; ACPI failure-path tests for missing or short buffers; verification that display and I2C muxes follow the selected GPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atpx_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.c

Purpose: implements Radeon HDMI/DisplayPort audio routing, register abstraction, infoframe programming, pin allocation, ELD notification, and DRM audio component binding across DCE generations.

Important APIs/functions/types: `radeon_audio_init`, `radeon_audio_detect`, `radeon_audio_mode_set`, `radeon_audio_dpms`, `radeon_audio_fini`, `radeon_audio_component_init`, and `radeon_audio_component_fini` are the main lifecycle and display hooks. `radeon_audio_endpoint_rreg/wreg` abstract endpoint register access. Internal function tables `radeon_audio_basic_funcs` and `radeon_audio_funcs` select generation-specific DCE/R600 operations. Helpers program SAD, speaker allocation, latency, DTO, AVI infoframes, ACR N/CTS values, VBI/audio packets, color depth, mute state, and pin selection.

Control flow: initialization checks the global `radeon_audio` option and DCE support, sets per-ASIC pin counts, initializes pin state, selects function tables, and disables all pins. Hotplug detection assigns HDMI or DP audio function tables based on connector type and DP sink type, allocates a pin for digital encoders with audio-capable displays, and enables/disables that pin. Mode set for HDMI mutes audio, writes EDID-derived audio blocks, sets clocks and packets, updates ACR/AVI infoframes, selects the pin, and unmutes; DP mode set programs the DP-specific subset with DTO based on VCO frequency. Component binding exposes ELD to the HDA audio driver and sends pin notifications after enable changes.

State and persistence: mutates `rdev->audio` state: enabled flag, pin array fields, generation function-table pointers, component registration flag, component pointer, and component mutex-protected state. Per-encoder `radeon_encoder->audio` and DIG `pin` assignments track connector audio routing. Hardware audio registers and endpoint state are programmed during mode set and DPMS. No filesystem persistence exists.

Dependencies and integration: uses DRM connector/encoder/mode helpers, EDID parsing (`drm_edid_to_sad`, `drm_edid_to_speaker_allocation`, ELD helpers), HDMI infoframe packing, Linux component framework, HDA `drm_audio_component`, and generation-specific helpers from `dce6_afmt.h`, `evergreen_hdmi.h`, `r600.h`, and related Radeon display code.

Risks: pin sharing requires careful enable-mask handling so one encoder does not disable a pin still used by another. EDID parsing failures can leave audio packets incomplete. The static `radeon_audio_acr` fallback result is shared and not reentrant, though display mode programming is normally serialized. Component binding depends on device links and correct mutex use. Generation function tables have optional callbacks, so missing callbacks must be tolerated without silently omitting required hardware programming.

Test signals: HDMI and DP audio playback after hotplug and mode changes; ELD visibility in the HDA driver; connector `has_audio` EDID variations; DP-to-HDMI sink type handling; DPMS on/off audio behavior; multi-monitor tests with shared pins; kernel warnings from ACR calculation and DRM errors from infoframe or SAD parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.h

Purpose: declares the Radeon audio abstraction used by core display code and generation-specific HDMI/DP audio implementations.

Important APIs/types/functions: `struct radeon_audio_basic_funcs` abstracts endpoint register reads/writes and pin enable; `struct radeon_audio_funcs` abstracts per-encoder audio operations such as pin selection, SAD/speaker allocation writes, latency fields, DTO, ACR, packet programming, mute, mode set, and DPMS. Public prototypes include audio lifecycle hooks, endpoint accessors, pin lookup, mode/DPMS handling, DFS divider decoding, and DCE3.2 helper functions. `RREG32_ENDPOINT` and `WREG32_ENDPOINT` route endpoint register access through `rdev->audio.funcs`.

Control flow: no runtime control flow is implemented in the header. It defines callback contracts consumed by `radeon_audio.c` and generation-specific files.

State and persistence: no state is stored here. The structs describe callbacks installed into `rdev->audio` and `radeon_encoder->audio` at runtime.

Dependencies and integration: includes Linux integer types and forward-declares `struct cea_sad`. It relies on Radeon/DRM types visible to including compilation units and is shared with DCE/R600 audio implementation files.

Risks: callback signature drift will break generation-specific implementations. The macros assume a local `rdev` variable exists, which is convenient but can be error-prone in new call sites. Optional callbacks require callers to null-check before use.

Test signals: kernel build coverage across all Radeon audio generation files; runtime HDMI/DP audio mode setting that exercises callback dispatch; static analysis for macro call sites and null callback handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_benchmark.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_benchmark.c

Purpose: provides a developer benchmark for Radeon buffer-object copy throughput across GTT and VRAM domains using DMA and/or blit copy engines.

Important APIs/functions: public `radeon_benchmark` dispatches benchmark scenarios by test number. `radeon_benchmark_move` allocates, reserves, pins, benchmarks, unpins, and releases source/destination BOs. `radeon_benchmark_do_move` repeatedly submits DMA or blit copies and waits on fences. `radeon_benchmark_log_results` reports throughput. Constants define copy method IDs, 1024 iterations, and a table of common display-mode-sized buffers.

Control flow: each requested test chooses domain pairs and buffer sizes. For each move, the code creates a source BO in the source domain and destination BO in the destination domain, pins both, runs DMA copy if available, runs blit copy if available, waits synchronously after each submitted fence, logs elapsed time in jiffies converted to milliseconds, and cleans up BO reservations/pins/references on all paths.

State and persistence: creates transient GPU buffer objects, fence objects, and reservation use during the benchmark. It does not persist results beyond DRM log output and does not alter long-lived driver state except normal BO/fence accounting and possible GPU engine activity.

Dependencies and integration: uses Radeon TTM BO helpers, GEM memory domain constants, copy engine hooks in `rdev->asic->copy`, fence wait/unref APIs, `jiffies`, and DRM logging. It is typically triggered by driver benchmark/debug paths rather than normal display operation.

Risks: synchronous fence waiting for 1024 iterations can take significant time and load the GPU. Throughput calculation divides by elapsed milliseconds only when nonzero, so very fast runs skip logging instead of reporting infinity. Cleanup reports a generic error based on the last `r` value, which may be overwritten by cleanup reservation attempts. Running on memory-pressure systems can fail BO allocation or pinning.

Test signals: manual benchmark invocation for test numbers 1-8; DRM log throughput lines for DMA and blit paths; error logs for unsupported copy methods or BO move failures; GPU hang/fence timeout monitoring under benchmark load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_bios.c

Purpose: locates, copies, validates, and classifies the Radeon video BIOS image from ACPI, PCI ROM, VRAM, disabled-ROM hardware paths, or platform ROM resources.

Important APIs/functions: public `radeon_get_bios` orchestrates BIOS retrieval and validates the result. Retrieval helpers include `radeon_atrm_get_bios`, `radeon_acpi_vfct_bios`, `igp_read_bios_from_vram`, `radeon_read_bios`, `radeon_read_disabled_bios`, and `radeon_read_platform_bios`. ASIC-family-specific disabled-ROM readers include `ni_read_disabled_bios`, `r700_read_disabled_bios`, `r600_read_disabled_bios`, `avivo_read_disabled_bios`, and `legacy_read_disabled_bios`. `radeon_atrm_call` fetches ACPI ATRM chunks.

Control flow: `radeon_get_bios` tries ACPI ATRM first for discrete hybrid GPUs, then ACPI VFCT, IGP VRAM copy, normal PCI ROM mapping, disabled-ROM register sequences, and platform ROM. After a candidate image is copied into `rdev->bios`, it checks the `0x55 0xaa` signature, rejects non-x86 ROMs, records `bios_header_start`, and sets `rdev->is_atom_bios` based on the `ATOM`/`MOTA` marker. Disabled-ROM paths save relevant display, bus, ROM, GPIO, PLL, and power registers, temporarily enable ROM access and disable conflicting display/VGA paths, read via `radeon_read_bios`, then restore registers.

State and persistence: allocates and owns `rdev->bios` in kernel memory, sets `rdev->bios_header_start`, and marks `rdev->is_atom_bios`. Temporarily mutates GPU registers while reading disabled ROMs but restores saved values before returning. ACPI table references are released with `acpi_put_table`; PCI ROM mappings are unmapped after copy. No disk persistence exists.

Dependencies and integration: depends on Linux PCI ROM mapping/resource APIs, ACPI ATRM/VFCT table access, I/O remapping, Radeon register definitions/macros, `radeon_card_posted`, and BIOS access macros such as `RBIOS8/16`. It feeds all later COMBIOS/AtomBIOS parsing, clock discovery, display setup, and PM table parsing.

Risks: hardware register sequencing is ASIC-specific and can affect display or ROM access if not restored exactly. Several firmware sources copy up to fixed or firmware-declared sizes and rely on signature checks after allocation. ACPI ATRM scanning must manage PCI device references correctly. VFCT parsing validates offsets but still trusts firmware structure contents. Failure to find a BIOS prevents normal driver initialization paths that require firmware tables.

Test signals: boot logs showing `ATOMBIOS detected` or `COMBIOS detected`; hybrid GPU systems using ATRM/VFCT; IGP systems booted behind discrete primary GPUs; ASIC-family tests where ROM BAR is initially disabled; validation of register restoration after failed and successful reads; negative tests for bad signatures, non-x86 ROM markers, and truncated ACPI VFCT entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_clocks.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_clocks.c

Purpose: reads, initializes, and controls legacy Radeon clock information, including PLL defaults, current engine/memory clocks, generic/Open Firmware fallbacks, legacy engine clock programming, and legacy clock gating.

Important APIs/functions: `radeon_legacy_get_engine_clock` and `radeon_legacy_get_memory_clock` compute current SCLK/MCLK from PLL registers. `radeon_get_clock_info` selects AtomBIOS, COMBIOS, Open Firmware, or generic fallback clock data and fills `rdev->clock` PLL ranges and `rdev->pm.current_*`. `radeon_legacy_set_engine_clock` programs the legacy SPLL for a requested engine clock via `calc_eng_mem_clock`. `radeon_legacy_set_clock_gating` toggles dynamic clocking/force-on bits across pre-AVIVO, R300, RS400/RS480, RV350+, and single-CRTC variants.

Control flow: clock info initialization first attempts firmware-specific clock discovery (`radeon_atom_get_clock_info` or `radeon_combios_get_clock_info`), then Open Firmware, then hard-coded generic defaults. It normalizes invalid reference dividers, sets PLL min/max/post-div constraints for pixel, display, system, and memory PLLs, and falls back to live register-derived clocks if default SCLK/MCLK are missing. Legacy engine-clock setting computes feedback/post dividers, switches to crystal input, sleeps/resets SPLL, programs feedback and gain, restarts PLL, selects post divider, and returns to normal clock input. Clock gating uses ASIC-family branches to clear or set force-on and dynamic-stop bits with required delays.

State and persistence: mutates `rdev->clock` PLL descriptors, default clocks, max pixel clock, display PLL data, and `rdev->pm.current_sclk/current_mclk`. Register programming changes hardware PLL and clock gating state. Open Firmware reads are transient. There is no filesystem persistence.

Dependencies and integration: uses DRM device-private Radeon state, AtomBIOS and COMBIOS clock readers, optional Open Firmware device tree properties, Radeon ASIC family predicates, low-level PLL/MMIO register macros, and PM hooks that later query or change clocks.

Risks: incorrect PLL divider calculations or reference frequencies can produce unstable clocks. Generic fallback values are approximate and may not match a board. Clock gating has many family/revision workarounds; changing force-on masks can cause hangs, especially around memory clocks and older VBIOS quirks. Busy delays make sequencing sensitive. Open Firmware property units are converted by division and assume expected firmware conventions.

Test signals: boot logs for firmware, OF, or generic clock source selection; validation of default/current SCLK/MCLK on legacy ASICs; modeset and PM transition tests after clock info initialization; stress tests with clock gating enabled/disabled; GPU hang monitoring after legacy engine clock changes; hardware register traces for family-specific gating paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_clocks.c -->
