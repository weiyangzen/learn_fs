# Research: subset-b-003711

Grouped source research for subset B work item `subset-b-003711`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_crtc.c

## Purpose
This file implements the Radeon AtomBIOS-backed CRTC helper path. It programs mode timings, overscan, scaler state, DPMS, pixel PLLs and spread spectrum, display engine PLL setup, framebuffer scanout registers, pageflip timing, power gating, and CRTC helper registration across legacy, AVIVO, and DCE4+ display hardware.

## Important APIs, Types, and Functions
The main exported entry points are `atombios_crtc_dpms`, `atombios_crtc_set_base`, `radeon_atom_disp_eng_pll_init`, `atombios_crtc_mode_set`, and `radeon_atombios_init_crtc`. Internal AtomBIOS wrappers include `atombios_overscan_setup`, `atombios_scaler_setup`, `atombios_lock_crtc`, `atombios_enable_crtc`, `atombios_enable_crtc_memreq`, `atombios_blank_crtc`, `atombios_powergate_crtc`, `atombios_set_crtc_dtd_timing`, `atombios_crtc_set_timing`, `atombios_crtc_program_ss`, `atombios_adjust_pll`, `atombios_crtc_set_disp_eng_pll`, and `atombios_crtc_program_pll`.

The scanout programming split is `dce4_crtc_do_set_base` for Evergreen/SI/CI-style registers, `avivo_crtc_do_set_base` for AVIVO/R600-era registers, and the legacy fallback `radeon_crtc_do_set_base`. PLL selection is handled by `radeon_get_pll_use_mask`, `radeon_get_shared_dp_ppll`, `radeon_get_shared_nondp_ppll`, and `radeon_atom_pick_pll`. The `atombios_helper_funcs` table connects the implementation to DRM CRTC helper callbacks.

## Control Flow
Modesetting starts in `atombios_crtc_mode_fixup`, which finds the encoder and connector bound to the CRTC, copies encoder output color state, runs Radeon scaling fixup, prepares the PLL parameters, then picks a hardware PPLL. `atombios_crtc_prepare` disables DCE6 CRTC power gating, locks double-buffered CRTC updates, and turns the CRTC off. `atombios_crtc_mode_set` programs the PLL, chooses DTD timing versus older timing tables depending on ASIC and TV/CV routing, sets the framebuffer base, applies overscan and scaler tables, resets the cursor, and records the hardware mode for dynamic power management. `atombios_crtc_commit` re-enables DPMS and unlocks CRTC updates.

PLL flow first builds `radeon_crtc->pll_flags` in `atombios_adjust_pll` based on ASIC family, output type, DP link rate, deep color, spread-spectrum requirements, and AtomBIOS `AdjustDisplayPll` table output. `atombios_crtc_set_pll` selects the relevant `struct radeon_pll`, computes dividers with the legacy or AVIVO PLL algorithm, disables spread spectrum for the target PLL, executes the versioned `SetPixelClock` parameter block, computes DCE4 spread-spectrum amount/step if needed, and re-enables spread spectrum. Shared PLL logic reuses a PPLL for DP outputs or matching non-DP clocks when the ASIC supports it, otherwise it allocates family-specific PPLL slots and returns `ATOM_PPLL_INVALID` when programming should be skipped or cannot be done safely.

Framebuffer-base flow pins the target GEM object into VRAM, reads tiling flags, translates DRM fourcc formats into display register depth/format/swap settings, disables VGA on the target pipe, writes primary and secondary surface addresses, programs pitch, viewport, desktop height, surface extents, graphics enable, and master update mode, unpins the old framebuffer if supplied, and calls `radeon_bandwidth_update`. DCE4+ additionally derives macrotile bank/tile-split/pipe configuration from Evergreen/SI/CI tile configuration arrays and supports high address registers. Both AVIVO and DCE4+ bypass the hardware LUT for 10-bit scanout formats to avoid truncation.

DPMS flow sets `radeon_crtc->enabled`, calls AtomBIOS CRTC enable/blank tables, manages DCE3 memory requests, toggles DRM vblank accounting, reloads LUTs, and recomputes power-management clocks. Disable flow unpins the current framebuffer, disables the graphics plane, optionally powergates DCE6, avoids shutting down a shared PLL still used by another enabled CRTC, disables eligible PPLLs, and clears CRTC encoder/connector/clock state.

## State and Persistence Behavior
Persistent display state lives mostly in `struct radeon_crtc`: `enabled`, `crtc_offset`, `pll_id`, `adjusted_clock`, `pll_flags`, `pll_reference_div`, `pll_post_div`, `bpc`, `ss_enabled`, `ss`, `encoder`, `connector`, `output_csc`, `hw_mode`, borders, and scaling type. The file mutates hardware state through AtomBIOS command tables and MMIO writes to CRTC, graphics, VGA, PLL, LUT, and viewport registers. It also changes BO pin state for scanout framebuffers and updates global mode state such as active vblank and bandwidth accounting.

The code intentionally preserves shared PLLs while another enabled CRTC still references them. It also stores the most recent adjusted mode in `hw_mode` for later DPM logic and keeps `pll_id = ATOM_PPLL_INVALID` as the sentinel for unallocated or externally clocked CRTC state.

## Dependencies and Integration Points
This file depends on DRM CRTC helper callbacks, `drm_display_mode` timing helpers, GEM framebuffer objects, Radeon BO reservation/pinning, tiling metadata, AtomBIOS command execution, Radeon PLL calculators, Radeon connector/encoder helpers, DP encoder-mode classification, cursor reset, LUT loading, vblank management, PM clock recomputation, display bandwidth calculation, and ASIC-family register definitions from Radeon headers. It is wired from `radeon_display.c` through `radeon_atombios_init_crtc`, and it collaborates tightly with `atombios_encoders.c` because encoder mode, selected CRTC source, DP link config, and PPLL ownership must agree.

## Risks
PLL selection is family-specific and fragile: a wrong shared-PPLL decision can blank an already active display, while `ATOM_PPLL_INVALID` is valid for DP external-clock cases but invalid for most non-DP encoders. AtomBIOS table version handling must match the firmware-provided parameter layout; unknown versions only log and return. Framebuffer pin/unpin error paths can leak pins or unpin the wrong old framebuffer if callers pass inconsistent state. Tiling field derivation depends on ASIC tile configuration arrays and framebuffer cpp, so incorrect metadata can produce corrupted scanout. The CRTC disable path must not disable a PLL used by another pipe. The DCE8 blanking workaround temporarily modifies VGA control and depends on restoring the original value. Interlaced viewport handling differs for Bonaire+ and is easy to regress.

## Test Signals
Useful signals include multi-monitor modesets across DVI/HDMI/DP/eDP/TV/VGA, hotplug with shared DP and non-DP PLL reuse, deep-color HDMI modes, 10-bit framebuffer scanout with LUT bypass, macro/micro tiled scanout on Evergreen/SI/CI, pageflip timing tests, suspend/resume with framebuffer reprogramming, DPMS on/off cycles with vblank accounting, DCE6 power-gating transitions, and mode validation on systems with external DP clocks. Kernel logs containing `Unknown table version`, `unable to allocate a PPLL`, unsupported formats, or clock recovery failures downstream indicate integration problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_dp.c

## Purpose
This file implements Radeon DisplayPort support through AtomBIOS AUX transactions, DPCD probing, DP link-rate/lane selection, sink power control, panel-mode selection, and DP link training. It bridges DRM DP helper APIs to Radeon AtomBIOS command tables and to the DIG encoder/transmitter setup code.

## Important APIs, Types, and Functions
Important exported functions are `radeon_atom_copy_swap`, `radeon_dp_aux_init`, `radeon_dp_getsinktype`, `radeon_dp_getdpcd`, `radeon_dp_get_panel_mode`, `radeon_dp_set_link_config`, `radeon_dp_mode_valid_helper`, `radeon_dp_needs_link_train`, `radeon_dp_set_rx_power_state`, and `radeon_dp_link_train`. Internal helpers include `radeon_process_aux_ch`, `radeon_dp_aux_transfer_atom`, `dp_get_adjust_train`, `convert_bpc_to_bpp`, `radeon_dp_get_dp_link_config`, `radeon_dp_encoder_service`, `radeon_dp_probe_oui`, `radeon_dp_update_vs_emph`, `radeon_dp_set_tp`, `radeon_dp_link_train_init`, `radeon_dp_link_train_finish`, `radeon_dp_link_train_cr`, and `radeon_dp_link_train_ce`.

The key local data structures are `union aux_channel_transaction`, which abstracts AtomBIOS AUX parameter versions, and `struct radeon_dp_link_train_info`, which carries the encoder, connector, DPCD, lane count, link clock, current training set, link status, training pattern support, and AUX channel through the training stages.

## Control Flow
AUX initialization records the connector HPD in the DDC bus record, selects native AUX for DCE5 only when `radeon_auxch` permits it, otherwise selects the AtomBIOS AUX transfer function, then initializes the DRM AUX object and marks the bus as AUX-capable. The AtomBIOS AUX transfer function formats a DP AUX request header, enforces the AtomBIOS write payload limit of 12 bytes and read limit of 16 bytes, calls `ProcessAuxChannelTransaction` under the channel and AtomBIOS scratch mutexes, translates AtomBIOS reply status to Linux errors, and stores the DP AUX reply nibble in `msg->reply`.

DPCD discovery reads `DP_RECEIVER_CAP_SIZE` bytes from the sink into the connector private DPCD cache, logs OUI data when supported, and clears `dpcd[0]` on failure. Link configuration chooses the lowest link rate/lane count combination that can carry the requested pixel clock at the monitor bpp, with a Nutmeg bridge special case fixed to 2.7 GHz. Mode validation reuses this calculation and rejects 5.4 GHz links when the connector is not DP 1.2-capable.

Link training starts only for DP/eDP sink types. It selects whether to use `DPEncoderService` or DIG encoder training commands based on the DPEncoderService command revision, builds the encoder/link identifier from DIG encoder and link selection, checks TPS3 support for DCE5, then runs initialization, clock recovery, channel equalization, and finish. Initialization powers the sink to D0, sets downspread and eDP panel mode, writes lane count and link bandwidth DPCD registers, starts source training, and disables sink training pattern. Clock recovery uses pattern 1, iteratively reads link status, detects max swing and repeated-voltage retry limits, applies sink-requested voltage/pre-emphasis to source and sink, and fails after unrecoverable conditions. Channel equalization uses TPS3 when supported, otherwise TPS2, repeats sink status reads and adjust requests, and stops after success or retry exhaustion. Finish disables training patterns on sink and source.

## State and Persistence Behavior
Persistent connector state is stored in `struct radeon_connector_atom_dig`: `dpcd`, `dp_sink_type`, `dp_lane_count`, and `dp_clock`. `radeon_dp_set_rx_power_state` writes sink DPCD power state for DP 1.1+ sinks and sleeps briefly for the transition. AUX transactions temporarily use the shared AtomBIOS scratch buffer and serialize access with `chan->mutex` plus `atom_context->scratch_mutex`. Link training mutates sink DPCD training registers and source DIG transmitter voltage/pre-emphasis state but does not persist its temporary `train_set` beyond the stack-local training info.

## Dependencies and Integration Points
The file depends on DRM DP helper functions for DPCD reads/writes, link-status decoding, delays, lane-count/link-rate parsing, and AUX registration. It calls AtomBIOS `ProcessAuxChannelTransaction` and `DPEncoderService`, uses Radeon I2C/AUX channel records, reads connector bridge IDs from `radeon_connectors.c`, consults monitor bpc, and calls DIG encoder/transmitter setup routines from `atombios_encoders.c`. Connector detect and mode-validation paths call the DPCD and link-config helpers, while encoder DPMS calls `radeon_dp_link_train` before video-on.

## Risks
AtomBIOS AUX uses a small scratch-buffer protocol with strict payload-size limits; oversized writes return `-E2BIG`, and incorrect endian handling on big-endian hosts would corrupt requests. The link budget calculation is simplified to `lane * rate * 8 / bpp` and does not model every transport overhead detail. Training loops rely on sink status and may fail on marginal cables, non-compliant sinks, or firmware command revisions. The `DPEncoderService` command revision workaround is critical because newer revisions cannot program training patterns correctly. Sink power-down is skipped for a Travis bridge quirk until a later point, so ordering changes can regress bridge panels. DPCD read failure clears the first DPCD byte and can make later logic treat the sink as incapable.

## Test Signals
Good signals include DP and eDP hotplug detection, DPCD cache population, AUX read/write transactions including zero-length and I2C-over-AUX requests, link validation for high pixel clocks and DP 1.2 5.4 GHz links, successful link training at 1/2/4 lanes and 1.62/2.7/5.4 GHz, TPS2/TPS3 behavior, eDP power sequencing, bridge adapters such as Nutmeg/Travis, and debug logs for voltage/pre-emphasis convergence. Failure signals include AUX timeout/errors, repeated `clock recovery failed`, `channel eq failed`, or mode rejection for clocks that should fit the sink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_encoders.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_encoders.c

## Purpose
This file implements AtomBIOS-backed Radeon encoder management. It creates DRM encoders from AtomBIOS object records, determines encoder modes, programs DAC/TV/DVO/LVDS/DIG/internal and external encoders, handles DIG transmitter routing and power sequencing, allocates DIG front-end encoders, manages LCD backlight control, controls HDMI/DP audio DPMS and mode setup, performs DAC load detection, and provides encoder helper callbacks for modesetting.

## Important APIs, Types, and Functions
Public entry points include `atombios_get_backlight_level`, `atombios_set_backlight_level`, `radeon_atom_backlight_init`, `atombios_dvo_setup`, `atombios_digital_setup`, `atombios_get_encoder_mode`, `atombios_dig_encoder_setup2`, `atombios_dig_encoder_setup`, `atombios_dig_transmitter_setup2`, `atombios_dig_transmitter_setup`, `atombios_set_edp_panel_power`, `radeon_atom_release_dig_encoder`, `radeon_atom_pick_dig_encoder`, `radeon_atom_encoder_init`, `radeon_atom_ext_encoder_setup_ddc`, `radeon_enc_destroy`, and `radeon_add_atom_encoder`.

Important internal helpers include the backlight ops, `radeon_atom_mode_fixup`, `atombios_dac_setup`, `atombios_tv_setup`, `radeon_atom_get_bpc`, `atombios_external_encoder_setup`, `atombios_yuv_setup`, `radeon_atom_encoder_dpms_avivo`, `radeon_atom_encoder_dpms_dig`, `radeon_atom_encoder_dpms`, `atombios_set_encoder_crtc_source`, `atombios_apply_encoder_quirks`, `radeon_atom_encoder_mode_set`, `atombios_dac_load_detect`, `radeon_atom_dac_detect`, `radeon_atom_dig_detect`, and the encoder `prepare`, `commit`, and `disable` callbacks.

The file uses several versioned AtomBIOS parameter unions: `union dvo_encoder_control`, `union lvds_encoder_control`, `union dig_encoder_control`, `union dig_transmitter_control`, `union external_encoder_control`, and `union crtc_source_param`.

## Control Flow
Encoder creation happens in `radeon_add_atom_encoder`. It merges duplicate AtomBIOS encoder objects by OR-ing supported devices, otherwise allocates `struct radeon_encoder`, sets possible CRTCs from `rdev->num_crtc`, assigns encoder IDs/devices/caps/default scaling, initializes a DRM encoder type, attaches private DAC or DIG/LVDS data, marks external encoders, and installs the appropriate helper function table. `radeon_atom_encoder_init` later sends transmitter-init commands for DIG transmitters and initializes external encoders on supported DCE generations.

Mode fixup sets the active device routing, computes CRTC timing info, applies interlace and vertical-front-porch workarounds, adjusts panel/TV/scaling modes, and calculates DP link config for DCE3+ digital outputs. Encoder prepare allocates or reassigns a DIG encoder, selects AFMT audio block where relevant, locks output routing, handles connector routers, powers eDP on for modeset, programs the CRTC source AtomBIOS table, and configures FMT blocks according to ASIC generation. Mode set turns the encoder off first, optionally programs AVIVO YUV routing, executes the per-encoder setup command, applies hardware quirks, and configures HDMI/DP audio. Commit turns the encoder on through DPMS and unlocks output routing. Disable turns DPMS off, disables the matching encoder tables, disables HDMI audio for HDMI, releases DIG encoders except MST, and clears active-device state.

DIG DPMS-on flow differs by generation. DCE4.1/DCE5 set panel mode, set up DIG encoder, and optionally external bridge setup; DCE4 sets up the DIG encoder; older DIG paths enable both encoder and transmitter. eDP is powered on before enabling the transmitter. DP outputs run link training and then DCE4+ video-on. LCD outputs restore GPU-controlled backlight or send LCD backlight-on. DPMS-off reverses this by video-off, external encoder disable, LCD backlight-off, sink power D3, transmitter disable, older encoder disable, and eDP panel power-off, with a Travis bridge quirk delaying sink D3. AVIVO DPMS uses output-control tables for TMDS/DVO/LVDS/LVTMA/DAC/TV/CV and handles LCD backlight through either the registered backlight device or AtomBIOS BLON/BLOFF commands.

Encoder-mode selection is connector-driven. It maps DVI/HDMI connectors to DVI or HDMI depending on digital routing, EDID HDMI/audio flags, and `radeon_audio`; DisplayPort connectors become DP or DP audio when the sink is native DP/eDP, otherwise fall back to HDMI/DVI through bridges; LVDS/eDP/VGA/TV map to their AtomBIOS modes. DAC load detection executes `DAC_LoadDetection` and reads BIOS scratch bits to report analog connector status. External DP bridge detection uses `ExternalEncoderControl` DAC load detection for DCE4 bridge CRT support.

DIG encoder allocation is family-specific. DCE6/DCE4 map transmitter/link to fixed front ends, DCE4.1 has Palm versus Llano behavior, DCE3.2 usually uses the CRTC id with Apple iMac exceptions, and DCE3 reserves DIG2 for LVTMA. The active encoder bitmask in `rdev->mode_info.active_encoders` tracks allocation and is released during disable or before reassignment.

## State and Persistence Behavior
The file mutates `struct radeon_encoder` fields such as `devices`, `active_device`, `pixel_clock`, `encoder_id`, `encoder_enum`, `rmx_type`, `underscan_type`, `caps`, `is_ext_encoder`, and `enc_priv`. DIG private state includes `dig_encoder`, `linkb`, `coherent_mode`, `panel_mode`, `afmt`, `bl_dev`, and `backlight_level`; DAC private state includes `tv_std`. Global display state includes `rdev->mode_info.active_encoders` and `rdev->mode_info.bl_encoder`. Hardware-visible state is stored in BIOS scratch registers for backlight level, connector load status, output/CRTC routing, and TV/CV active status, plus AtomBIOS-programmed encoder/transmitter/output state.

Backlight registration creates a Linux backlight device for GPU-controlled AtomBIOS panels when ACPI policy allows native control, stores the device in DIG private state, initializes brightness from scratch registers, and unregisters it in encoder destruction. eDP panel power sequencing persists in connector private `edp_on` state as used by detect and DPMS paths.

## Dependencies and Integration Points
This file integrates with DRM encoder helper callbacks, DRM connector/EDID/audio information, Linux backlight and ACPI video policy, DMI/PCI quirks, AtomBIOS command parsing/execution, Radeon connector routing, Radeon CRTC state, DP link training from `atombios_dp.c`, HDMI/DP audio helpers, FMT programming helpers from DCE/AVIVO display code, output locks and scratch-register helpers from Radeon AtomBIOS support, HPD sensing, external encoder lookup, router selection, and the mode_config encoder list. It is initialized from Radeon display/device setup and called throughout legacy DRM modesetting.

## Risks
The file is highly table-version-sensitive: DVO, LVDS, DIG encoder, transmitter, external encoder, and CRTC-source command layouts all vary by firmware revision. Many branches encode ASIC-generation routing rules, so a wrong family check can select the wrong DIG front end, PHY, link, PLL source, HPD, or lane count. Backlight ownership must honor Apple gmux and ACPI native-backlight policy to avoid duplicate controls. DP/eDP power sequencing and Travis/Nutmeg bridge quirks are ordering-sensitive. Shared pre-DCE3 encoders can be in use by another connector, so disable must avoid shutting them down prematurely. Active encoder bitmask updates are simple and log conflicts rather than resolving them, making modeset ordering important. Connector lookup fallbacks during init can produce different encoder modes than active modeset paths if connector state is incomplete.

## Test Signals
Important signals include encoder creation from AtomBIOS object tables, LVDS/eDP backlight registration and brightness persistence, DP/eDP modeset with link training and panel power, HDMI/DVI mode selection with and without audio, DAC/TV/CV load detection from scratch bits, external DP bridge DDC and DAC-load setup, multi-monitor modesets that stress DIG encoder allocation, MST disable behavior, DCE3/DCE4/DCE5/DCE6/DCE8 family coverage, suspend/resume with output scratch restoration, and kernel logs for unknown AtomBIOS table versions, active encoder conflicts, or failed backlight registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_i2c.c

## Purpose
This file implements a Radeon I2C adapter backend that routes I2C transfers through the AtomBIOS `ProcessI2cChannelTransaction` command table. It provides hardware-assisted I2C for display DDC and related AtomBIOS-controlled buses.

## Important APIs, Types, and Functions
The exported adapter callbacks are `radeon_atom_hw_i2c_xfer` and `radeon_atom_hw_i2c_func`, declared in `atom.h` and installed in `radeon_i2c.c`. The key internal helper is `radeon_process_i2c_ch`, which builds `PROCESS_I2C_CHANNEL_TRANSACTION_PS_ALLOCATION`, locks the I2C channel and AtomBIOS scratch buffer, executes the AtomBIOS command, and copies read data back to the caller.

The file defines `TARGET_HW_I2C_CLOCK` as 50 kHz and enforces AtomBIOS command limits of three bytes per write transaction and 255 bytes per read transaction.

## Control Flow
`radeon_atom_hw_i2c_xfer` first detects the Linux I2C bus-probe pattern of a single zero-length message and turns it into a zero-byte hardware write transaction. For normal transfers it walks each `i2c_msg`, chooses read or write flags, selects the maximum chunk size based on AtomBIOS limits, and loops until the message length is consumed. Each chunk calls `radeon_process_i2c_ch`; any error aborts the whole transfer and a fully successful batch returns the original message count.

For writes, `radeon_process_i2c_ch` treats `buf[0]` as the register index, reduces the transaction byte count by one, copies up to the remaining two bytes into a little-endian 16-bit output field, and rejects attempts above the three-byte AtomBIOS write limit. For reads, it sets register index and output pointer to zero, lets AtomBIOS write read data into its scratch area, then uses `radeon_atom_copy_swap` to copy from scratch to the caller buffer. It shifts the 7-bit slave address left one bit for the AtomBIOS table and uses the channel record's I2C line number.

## State and Persistence Behavior
No long-lived software state is owned here. The code temporarily mutates the shared AtomBIOS scratch buffer and serializes it with `rdev->mode_info.atom_context->scratch_mutex`; it also serializes the I2C channel with `chan->mutex`. Hardware-visible effects are the I2C transactions performed by firmware on the selected I2C line. `radeon_atom_hw_i2c_func` advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL` capability to the I2C core.

## Dependencies and Integration Points
This file depends on Linux I2C adapter/message types, Radeon I2C channel records, the DRM device's `dev_private` Radeon device, AtomBIOS command execution through `atom_execute_table_scratch_unlocked`, AtomBIOS scratch memory, and `radeon_atom_copy_swap` from `atombios_dp.c` for endian-safe data movement. It is integrated by the Radeon I2C layer as the master transfer implementation for AtomBIOS hardware I2C channels used by connector probing and DDC reads.

## Risks
The AtomBIOS write format supports only a register byte plus up to two payload bytes, so callers expecting arbitrary I2C block writes will fail with `-EINVAL`. Read and write chunking changes large Linux I2C messages into multiple firmware transactions, which may not be equivalent for devices requiring repeated-start semantics across a longer write. Error reporting is coarse: any non-success firmware status becomes `-EIO`. The helper assumes the channel record line number and scratch buffer are valid and depends on lock ordering matching other AtomBIOS users. Big-endian correctness depends on the shared `radeon_atom_copy_swap` behavior.

## Test Signals
Useful tests include DDC EDID reads over AtomBIOS hardware I2C, zero-length bus probes, multi-message register-read sequences, reads larger than 255 bytes split into chunks, write rejection above three bytes, concurrent DDC/AUX activity across multiple connectors, and logs showing `hw_i2c error` or oversized write attempts. Build coverage should also ensure the callbacks match the signatures in `atom.h` and the adapter setup in `radeon_i2c.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/avivod.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/avivod.h

## Purpose
This header provides a small set of AVIVO-era display and VGA register offsets and bit masks used by Radeon display initialization, suspend/resume, power management, and low-level modeset code. It covers CRTC enable/status/update-lock registers, graphics surface address registers, VGA control registers, VGA memory control, and VGA render status masking.

## Important APIs, Types, and Functions
There are no functions or types. The exported constants include `D1CRTC_CONTROL`, `CRTC_EN`, `D1CRTC_STATUS`, `D1CRTC_UPDATE_LOCK`, `D1GRPH_PRIMARY_SURFACE_ADDRESS`, `D1GRPH_SECONDARY_SURFACE_ADDRESS`, equivalent D2 CRTC/graphics-address registers, `D1VGA_CONTROL`, `D2VGA_CONTROL`, `VGA_HDP_CONTROL`, `VGA_MEMORY_BASE_ADDRESS`, `VGA_RENDER_CONTROL`, and bit masks such as `DVGA_CONTROL_MODE_ENABLE`, `DVGA_CONTROL_TIMING_SELECT`, `DVGA_CONTROL_SYNC_POLARITY_SELECT`, `DVGA_CONTROL_OVERSCAN_TIMING_SELECT`, `DVGA_CONTROL_OVERSCAN_COLOR_EN`, `DVGA_CONTROL_ROTATE`, `VGA_MEM_PAGE_SELECT_EN`, `VGA_MEMORY_DISABLE`, `VGA_RBBM_LOCK_DISABLE`, `VGA_SOFT_RESET`, and `VGA_VSTATUS_CNTL_MASK`.

## Control Flow
The header has no executable control flow. Its values are consumed by C files that perform register reads and writes through Radeon MMIO helpers. Typical flows include disabling legacy VGA memory before ASIC initialization, checking whether CRTC pipes are enabled, saving/restoring VGA HDP control across suspend, and programming or preserving AVIVO display state.

## State and Persistence Behavior
The header stores no runtime state. It names persistent hardware registers whose contents survive across parts of the driver lifecycle until overwritten or reset by hardware/firmware. Consumers use these definitions to mutate VGA memory aperture behavior, CRTC enable state, update locks, and graphics surface addresses.

## Dependencies and Integration Points
Consumers include `radeon_pm.c`, `r600.c`, `rv770.c`, `evergreen.c`, `cik.c`, `rv515.c`, `rs600.c`, `radeon_device.c`, and display modeset code that also uses broader register headers such as `r500_reg.h`, `evergreen_reg.h`, `cikd.h`, or ASIC-specific `*d.h` files. The constants integrate with `RREG32`/`WREG32` MMIO accessors and with save/restore structures in family-specific initialization code.

## Risks
Because the header defines raw numeric offsets, any mismatch with ASIC generation or duplicate definitions in other register headers can lead to writes to the wrong display register. The short names lack the `AVIVO_` prefix used by some parallel definitions, so include ordering and naming collisions matter. These registers affect VGA memory decode and CRTC enablement, so incorrect use can blank displays, break resume restore, or expose legacy VGA aperture behavior unexpectedly.

## Test Signals
Build coverage across AVIVO/R600/RV770/Evergreen/CIK code checks macro availability and naming conflicts. Runtime signals include successful ASIC initialization with VGA memory disabled, suspend/resume preserving scanout, CRTC enabled-state detection during PM, and absence of display blanking when VGA HDP and CRTC control registers are touched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/avivod.h -->
