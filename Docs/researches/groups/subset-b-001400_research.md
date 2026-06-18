# Research: subset-b-001400

Grouped research for AMD DCN DIO link and stream encoder files. Each section is keyed by the original source path and is intended to split directly into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.h

## Purpose
This header defines the DCN2 stream-encoder register surface and exported helper prototypes that later DIO stream encoders build on. It does not implement runtime control flow; its main role is to bind the generic `stream_encoder` and `dcn10_stream_encoder` abstractions to DCN2-specific registers, masks, and stream helper functions.

## Important APIs, Types, and Macros
`SE_DCN2_REG_LIST(id)` extends common stream encoder registers with HDMI generic packet controls, DP DSC controls, dynamic metadata (`DME_CONTROL`, `DP_SEC_METADATA_TRANSMISSION`, `HDMI_METADATA_PACKET_CONTROL`), and `DP_SEC_FRAMING4`. `SE_COMMON_MASK_SH_LIST_DCN20(mask_sh)` adds field mappings for HDMI packet slots 0-7, DSC mode/slice/bytes-per-pixel, VBID6 PPS timing, metadata engine fields, Dolby Vision enable, DP pixel combine, adaptive-sync SDP line programming, and SDP splitting.

The exported functions are `dcn20_stream_encoder_construct`, `enc2_stream_encoder_dp_set_stream_attribute`, `enc2_stream_encoder_dp_unblank`, `enc2_set_dynamic_metadata`, and `enc2_get_fifo_cal_average_level`. Later DCN30+ implementations reuse these function pointers for DP stream attributes, DP unblank behavior in some generations, dynamic metadata, and FIFO diagnostics.

## Control Flow and State
No executable control flow lives here. The macros become compile-time initializers for per-instance register tables and mask/shift tables. The persistent state affected by functions declared here is hardware state in DIG/DP/DME blocks, reached through implementations elsewhere.

## Dependencies and Integration Points
The file depends on `stream_encoder.h` and `dcn10/dcn10_stream_encoder.h`. It is included by DCN30, DCN314, DCN32, and DCN35 stream encoder headers, making this header a compatibility bridge between DCN1 base helpers and DCN2+ metadata/DSC behavior.

## Risks and Test Signals
Risk is concentrated in register-field accuracy: any renamed or omitted mask entry breaks later `REG_UPDATE`/`REG_GET` users at compile time or, worse, writes the wrong hardware field. Useful test signals are kernel build coverage for generated register tables, DP DSC enable/disable, HDR metadata on DP/HDMI, adaptive-sync SDP line placement, Dolby Vision metadata, and FIFO average-level reporting on DCN2-derived encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.c

## Purpose
This file implements the baseline DCN3 DIO link encoder. It constructs a `dcn20_link_encoder`/`dcn10_link_encoder` object with DCN30 function pointers, initializes AUX/TMDS hardware, advertises output signal support, maps transmitters to preferred DIG engines, and imports link capabilities from VBIOS.

## Important APIs and Functions
`dcn30_link_encoder_validate_output_with_stream` delegates stream validation to the DCN10 implementation. `dcn30_link_enc_funcs` mostly reuses DCN10/DCN20 operations, with DCN30-specific `enc3_hw_init`, FEC hooks from DCN2, and DP/HDMI capability accessors. `dcn30_link_encoder_construct` fills the base object, register pointers, HPD/AUX register blocks, output signals, preferred engine, feature flags, and VBIOS-derived capability bits. `enc3_hw_init` writes hard-coded AUX DPHY RX/TX control values, sets legacy `TMDS_CTL0`, and calls `dcn10_aux_initialize`.

## Control Flow
Construction is linear: copy initialization data, choose `preferred_engine` from the UNIPHY transmitter, set HDMI 6 Gb/s default true, query `get_encoder_cap_info`, overwrite HBR2/HBR3/HDMI/DP2/UHBR/USB-C feature bits if the BIOS query succeeds, then respect `debug.hdmi20_disable`. Hardware init programs AUX electrical timing before enabling the common AUX machinery.

## State and Persistence
The object persists feature capability state in `enc10->base.features`, register table pointers, connector/HPD identities, and preferred DIG routing. Runtime hardware state persists in AUX DPHY registers and `TMDS_CTL_BITS`.

## Dependencies and Integration Points
It depends on `reg_helper.h`, `core_types.h`, `link_encoder.h`, `stream_encoder.h`, `dc_bios_types.h`, GPIO service interfaces, DCN20 helpers, and VBIOS callbacks. Display Core uses the function table through `struct link_encoder_funcs` during mode set, DP training, MST allocation, HPD handling, FEC, PSR packets, and link capability evaluation.

## Risks and Test Signals
Primary risks are wrong transmitter-to-DIG mapping, stale VBIOS capability fields, and hard-coded AUX DPHY values that may not fit all boards. Tests should cover HDMI 2.0 disable override, HBR2/HBR3/UHBR capability advertisement, USB-C capability propagation, AUX transactions after init, HPD filtering, DP SST/MST enable/disable, FEC state, and kernel build coverage for all referenced function pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h

## Purpose
This header defines the DCN30 link encoder register and mask/shift contract plus constructor and hardware-init prototypes. It gives the DCN30 implementation and later derivatives a common DIO backend register list for DIG, DP, AUX, DPCS, HPD, FEC, and PHY/alt-mode fields.

## Important APIs, Types, and Macros
`LE_DCN3_REG_LIST(id)` enumerates the DIG backend, TMDS, DP DPHY, DP link/framing, MST SAT, secondary packet, video stream, fast-training, and HBR2 pattern registers. `LINK_ENCODER_MASK_SH_LIST_DCN30(mask_sh)` extends DCN20 with TMDS DC balancer control. `DPCS_DCN3_MASK_SH_LIST(mask_sh)` adds DPCS data-order, PHY boost, TX clock enable, and USB-C DP alt-mode lane/disable fields.

The prototypes are `dcn30_link_encoder_construct`, `enc3_hw_init`, and `dcn30_link_encoder_validate_output_with_stream`.

## Control Flow and State
The header itself has no runtime flow. It shapes the static register tables consumed by `dcn30_dio_link_encoder.c` and compatible later files. State is hardware register state accessed through generated table pointers and masks.

## Dependencies and Integration Points
The header includes `dcn20/dcn20_link_encoder.h` and is included by DCN31/DCN32/DCN35/DCN401 link encoder headers or implementations. It is a foundational include for DCN3 link function-table construction.

## Risks and Test Signals
Any mismatch in register list or mask names will break compile-time generated register binding or cause runtime writes to the wrong field. Test signals include successful all-ASIC builds, DP link training, TMDS output, MST allocation, AUX init, FEC toggling, and USB-C DP alt-mode detection paths using the DPCS fields defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c

## Purpose
This file implements the baseline DCN30 DIO stream encoder. It programs HDMI and DP info packets, DSC PPS secondary data packets, HDMI/DVI stream attributes, audio packet setup, and the DCN30 `stream_encoder_funcs` table used by display mode set paths.

## Important APIs and Functions
`enc3_update_hdmi_info_packet` writes a VPG generic packet and maps hardware packet indices 0-14 to HDMI generic packet control and line registers. `enc3_stream_encoder_update_hdmi_info_packets` enables HDMI DB/audio clocking and programs AVI, HF-VSIF, gamut, vendor, SPD, HDR static metadata, and VTEM packets. `enc3_stream_encoder_stop_hdmi_info_packets` clears all generic HDMI packet slots.

`enc3_stream_encoder_update_dp_info_packets` writes VSC, SPD, HDR, and adaptive-sync SDPs through VPG and enables `DP_SEC_GSP*` bits plus master `DP_SEC_STREAM_ENABLE`; it also preserves stream enable when dynamic metadata is already active. `enc3_stream_encoder_update_dp_info_packets_sdp_line_num` moves adaptive-sync SDP to an OTG-referenced line when valid. `enc3_dp_set_dsc_config`, `enc3_dp_set_dsc_pps_info_packet`, and `enc3_read_state` handle DSC mode, PPS packet fragments in GSP11-14, VBID6 timing, and DSC debug readback.

HDMI/DVI setup functions either call VBIOS `encoder_control` or directly set DIG clock pattern and reset DIG FIFO through `DIG_START` when BIOS execution is avoided. HDMI setup configures deep color, scrambling for 340 MHz and above, general-control/null/audio packets, audio infoframe line, and AVMUTE. Audio helpers delegate to AFMT and program DP/HDMI audio registers, ACR/N/CTS values, and DP timestamps.

## Control Flow
The function table wires base DCN2 DP stream attributes and dynamic metadata to DCN30-specific HDMI packet, DP packet, DSC, and audio handlers. Constructor initialization is simple pointer assignment: context, BIOS, engine id, VPG, AFMT, register tables, shift/mask tables, and stream encoder instance.

## State and Persistence
Persistent state is entirely hardware-facing: HDMI generic packet controls, VPG packet RAM, DP secondary-packet enables, DSC mode/PPS/VBID registers, AFMT audio state, HDMI ACR registers, DIG reset state, and base object pointers. There is no heap allocation or software cache besides the initialized object.

## Dependencies and Integration Points
The file integrates with VPG (`update_generic_info_packet`), AFMT audio callbacks, DC BIOS encoder control, DC debug flags, `reg_helper` register macros, DCN1/DCN2 helper functions, audio clock calculation, DP trace/metadata infrastructure, and the public `stream_encoder` function table used by link/programming code.

## Risks and Test Signals
Risks include incorrect packet-index mapping, duplicate VSC writes at DP packet index 1, stale TODO behavior for PSR-SU VSC packets, HDMI scrambling/deep-color mismatches, DSC PPS line ordering relative to VBID6, and reliance on VBIOS unless `avoid_vbios_exec_table` is set. Test signals should include HDMI infoframe presence/stop, DP VSC/HDR/adaptive-sync SDP capture, DSC PPS packet capture, HDMI audio ACR validation at common pixel clocks, DP audio enable, DVI RGB/8bpc assertions, and register readback through `enc_read_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h

## Purpose
This header exposes the DCN30 DIO stream encoder register/mask surface and shared `enc3_*` helper prototypes. Later stream encoder implementations include it to reuse HDMI/DP packet, DSC PPS, and audio behavior.

## Important APIs, Types, and Macros
`SE_DCN3_REG_LIST(id)` lists the DCN30 DIG, HDMI, DP, AFMT, DME, metadata, DSC, FIFO-status, and clock-pattern registers. `SE_COMMON_MASK_SH_LIST_DCN30(mask_sh)` maps fields for DP pixel format, HDMI control, generic HDMI packet slots 0-14, MST rate, DP secondary packets, DP stream enable/status, DP VID M/N, DIG start/source, HDMI/DP audio, DSC, metadata, Dolby Vision, FIFO diagnostics, SDP splitting, and clock pattern. The file also defines compatibility bit names for RDPCSTX/DPCSTX fields whose names changed.

Public prototypes include `dcn30_dio_stream_encoder_construct`, HDMI packet update/stop helpers, DP SDP update helpers, AFMT/audio wrappers, DSC PPS programming, and single HDMI packet update.

## Control Flow and State
No runtime flow is defined here. Its macros produce register access tables used by `REG_UPDATE`, `REG_GET`, and `REG_SET` in DCN30 and descendant implementations. State is DIG/DP/HDMI/AFMT/DME hardware state.

## Dependencies and Integration Points
The header includes `dcn30_vpg.h`, `dcn30_afmt.h`, `stream_encoder.h`, and `dcn20_stream_encoder.h`. It is used by DCN30, DCN314, DCN32, and DCN35 stream encoder C files and headers.

## Risks and Test Signals
Risk lies in large mask-list drift: missing packet, DSC, FIFO, or audio fields can break dependent generations. Test signals include full compile coverage, HDMI packet slots 8-14, DP GSP11 PPS, dynamic metadata, DP audio, HDMI audio, FIFO diagnostics, and any ASIC-specific register-generation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c

## Purpose
This file implements a DCN301 link encoder variant. It is structurally close to DCN30 but uses a distinct function table and a narrower VBIOS feature import path.

## Important APIs and Functions
`dcn301_link_enc_funcs` wires common DCN10/DCN20 operations, `enc3_hw_init`, FEC hooks, DCN20 alt-mode and max-link-cap helpers, HPD operations, and DPCD/PSR helpers. `dcn301_link_encoder_construct` initializes the base object, output signal mask, register pointers, transmitter-to-DIG preferred engine mapping, HDMI default capability, and VBIOS capability overrides.

## Control Flow
Construction copies init fields, sets `preferred_engine` for UNIPHY A-G, sets HDMI 6 Gb/s true by default, calls `get_encoder_cap_info`, then imports only HBR2, HBR3, HDMI 6 Gb/s, and USB-C capability bits. It does not import DP2/UHBR fields like DCN30. The debug `hdmi20_disable` flag clears HDMI 6 Gb/s after VBIOS parsing.

## State and Persistence
The persistent object state is the same base link encoder structure: context, encoder id, HPD/connector identities, feature flags, transmitter, preferred engine, and register/mask pointers. Hardware init is delegated to DCN30 `enc3_hw_init`.

## Dependencies and Integration Points
The implementation depends on DCN301 header definitions, DCN20/DCN10 link helpers, VBIOS functions, GPIO, and the shared `link_encoder_funcs` interface. It integrates into display resource construction for DCN301 ASICs.

## Risks and Test Signals
The main risk is capability skew from DCN30 because DP2/UHBR bits are intentionally absent in the VBIOS import. Tests should validate connector capability reporting, HDMI 6 Gb/s disable, AUX init through `enc3_hw_init`, DP SST/MST operation, FEC, HPD, and all expected DCN301 board transmitters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.h

## Purpose
This header defines DCN301 link encoder register lists, mask/shift additions, and construction prototypes. It parallels DCN30 while adding DCN301-specific DPCS mask fields.

## Important APIs, Types, and Macros
`LE_DCN301_REG_LIST(id)` enumerates DIG backend, TMDS, DP DPHY/link/MST/secondary/stream/fast-training registers. `LINK_ENCODER_MASK_SH_LIST_DCN301(mask_sh)` extends DCN20 with `TMDS_SYNC_DCBAL_EN`. `DPCS_DCN301_MASK_SH_LIST(mask_sh)` includes HDMI FRL mode, 10-bit data swap, 18-bit data-order invert, PHY boost, and TX clock enable.

The header declares `dcn301_link_encoder_construct` and the shared `enc3_hw_init`.

## Control Flow and State
There is no executable flow. The macros become static register binding data used by the C implementation and resource initialization. Hardware state is reached through the generated register and mask tables.

## Dependencies and Integration Points
It includes `dcn20/dcn20_link_encoder.h` and integrates with DCN301 resource construction, shared DCN30 AUX initialization, and common DCN10/DCN20 link functions.

## Risks and Test Signals
Register-list drift is the main risk, especially FRL/data-swap fields that differ from DCN30. Test signals include compile-time register generation, HDMI FRL-related path coverage if applicable, TMDS link behavior, DP link training, FEC, and AUX transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c

## Purpose
This file implements the DCN31 link encoder, extending DCN30 with DIO PHY muxing for HPO encoders, DMUB-based USB-C DP Alt Mode queries, mappable link encoder/DPIA handling, minimal link encoder construction, and DCN31 AUX initialization behavior.

## Important APIs and Functions
`phy_id_from_transmitter`, `has_query_dp_alt`, and `query_dp_alt_from_dmub` translate a UNIPHY transmitter to DMUB query data and decide whether to use the newer firmware interface. `dcn31_link_encoder_set_dio_phy_mux` writes `DIO_LINK[A-F]_CNTL` fields for legacy DIO, HPO DP 128b/132b, or HDMI FRL encoder selection. `enc31_hw_init` avoids hard-coded AUX DPHY programming because DMUB reads it from VBIOS, but still sets legacy `TMDS_CTL0` and initializes AUX.

The function table overrides DP SST/MST enable, disable, alt-mode detection, max-link-cap query, and DIO PHY mux. `dcn31_link_encoder_construct` initializes object state and imports HBR2/HBR3/HDMI/DP2/UHBR/USB-C flags from VBIOS. `dcn31_link_encoder_construct_minimal` creates a DP-only encoder object without a full `dc_link`. DPIA helpers build `DMUB_CMD__DPIA_DIG1_DPIA_CONTROL` commands for USB4/retimer-style mappable encoders.

## Control Flow
For normal DP enable/disable, DCN31 checks `link_enc_cfg_is_transmitter_mappable`. Non-mappable encoders fall back to DCN20/DCN10 DP paths. Mappable encoders configure the encoder locally, discover the `dc_link` using the preferred engine, populate DMUB DPIA control data with action, encoder id, SST/MST mode, lane count, symbol clock, HPD placeholder, DPIA id, and FEC readiness, then execute a DMUB command. Disable mirrors this flow and clears DP training complete.

Alt-mode and max-capability flow first rejects non-USB-C encoders. If supported firmware is available, it uses DMUB query response fields; otherwise it reads RDPCSTX/RDPCSPIPE PHY fields with Yellow Carp B0-specific register selection. USB-C shared-lane mode caps DP lane count to two when DP4 is not active.

## State and Persistence
State persists in the link encoder object, VBIOS-derived feature bits, DIO link mux registers, AUX initialization state, DP training-complete register, DMUB-controlled DPIA link state, and USB-C alt-mode PHY/firmware state. The code does not allocate memory.

## Dependencies and Integration Points
Dependencies include `link_enc_cfg`, `dc_dmub_srv`, `dal_asic_id`, `link_service`, DCN30 link helpers, VBIOS callbacks, and common DCN10/DCN20 link implementations. Integration is broad: DP enable/disable, USB4 DPIA, HPO routing, FEC readiness via `link_srv`, and USB-C lane limit decisions.

## Risks and Test Signals
Risks include firmware-version gating for DMUB alt queries, legacy register reads that may hang if DMUB is not running, null `dc_link` lookup on mappable paths, incorrect HPO instance routing, and divergent B0 PHY register selection. Test signals should cover non-mappable and mappable DP SST/MST, DPIA enable/disable DMUB command payloads, FEC readiness propagation, USB-C DP4 versus 2-lane limiting, Yellow Carp B0 alt-mode detection, minimal encoder construction, and HPO DP/HDMI mux programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h

## Purpose
This header defines DCN31 link encoder register/mask extensions and public APIs for DIO PHY muxing, mappable DP/DPIA flows, USB-C alt-mode checks, and max-link-cap derivation.

## Important APIs, Types, and Macros
`LE_DCN31_REG_LIST(id)` extends DCN3 with `DP_DPHY_INTERNAL_CTRL` and DIO link control registers A-F. `LINK_ENCODER_MASK_SH_LIST_DCN31(mask_sh)` includes FEC fields, TMDS control, AUX DPHY fields, and DIO link encoder selection fields. `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(mask_sh)` define extensive RDPCSTX/RDPCSPIPE PHY, PLL, FIFO, DP alt-mode, fuse, and interrupt fields. `DPCS_DCN314_REG_LIST(id)` provides a related reduced PHY register list for DCN314 resources.

Public APIs include full and minimal constructors, `dcn31_link_encoder_set_dio_phy_mux`, DP SST/MST enable, disable, `dcn31_link_encoder_is_in_alt_mode`, `dcn31_link_encoder_get_max_link_cap`, and `enc31_hw_init`.

## Control Flow and State
The header defines contracts only. Runtime users program DIO mux, AUX, DP PHY/FEC, and alt-mode state through the listed registers and function prototypes.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h`. DCN32, DCN35, and DCN401 reuse DCN31 DIO mux and alt-mode APIs, so this header is a cross-generation link-routing dependency.

## Risks and Test Signals
The field surface is large and ASIC-sensitive; incorrect PHY or alt-mode fields can break USB-C lane detection, DP training, or power sequencing. Test signals include all DCN31-family builds, HPO mux programming, FEC status, USB-C DP Alt Mode detection, DP lane limiting, AUX init, and DP PHY training across transmitters A-F.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.c

## Purpose
This file implements the DCN314 stream encoder, a DCN30-derived stream encoder with explicit DIG FIFO control and revised DP unblank/DSC behavior for newer register definitions.

## Important APIs and Functions
`enc314_reset_fifo`, `enc314_enable_fifo`, `enc314_disable_fifo`, and `enc314_is_fifo_enabled` control `DIG_FIFO_CTRL0`, wait on `DIG_FIFO_RESET_DONE` when `DIG_SYMCLK_FE_ON` is active, and program read-start level `0x7`. `enc314_dp_set_odm_combine` uses `DP_PIXEL_PER_CYCLE_PROCESSING_MODE` rather than the older `DP_PIXEL_COMBINE`.

The DVI and HDMI attribute functions mirror DCN30 VBIOS/direct setup but call `enc314_enable_fifo` when direct programming is used. HDMI setup repeats DCN30 deep-color, scrambling, audio-infoframe, and AVMUTE programming. `enc314_stream_encoder_dp_blank` can disable FIFO after DP video stream disable when `debug.dig_fifo_off_in_blank` is set. `enc314_stream_encoder_dp_unblank` computes initial M/N, handles 4:2:0, DSC 4:2:2, and ODM/OPP combining, disables DP video, resets steer FIFO, enables DP stream, then explicitly enables the DIG resync FIFO.

`enc314_dp_set_dsc_config` only toggles `DP_DSC_MODE` because bytes-per-pixel and slice-width registers were removed in newer hardware. `enc314_read_state` omits removed DSC fields. `enc314_set_dig_input_mode` maps a two-pixel container to `DIG_FIFO_OUTPUT_PIXEL_MODE`.

## Control Flow
The DCN314 function table keeps DCN30 packet/audio helpers but overrides HDMI/DVI attributes, DP blank/unblank, ODM combine, DSC config/readback, FIFO hooks, and input mode. Constructor initialization follows the standard stream encoder pointer assignment pattern.

## State and Persistence
Persistent state includes DIG FIFO enable/reset/read-level, DP stream enable/status, DP VID M/N timing, DP pixel-per-cycle mode, DSC mode, PPS packet registers, HDMI controls, AFMT audio state, and debug-flag-driven FIFO state across blank/unblank.

## Dependencies and Integration Points
The file depends on DCN30 stream helpers, `link_service` for DP trace sequencing, `dpcd_defs`, VBIOS encoder control, AFMT/VPG callbacks, and DC debug flags. It integrates with link programming through the `stream_encoder_funcs` table.

## Risks and Test Signals
Risks center on FIFO sequencing: enabling too early or disabling at blank can corrupt video if clocks are not stable. Removed DSC fields require callers not to rely on bytes-per-pixel/slice-width writes. Tests should cover DP unblank with 1/2 pixels per cycle, ODM/OPP >1, DSC 4:2:2 simple and non-simple, `dig_fifo_off_in_blank`, HDMI direct and VBIOS setup, FIFO reset wait when symclk is off, and DSC state readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.h

## Purpose
This header defines the DCN314 stream encoder register/mask surface and exposes the DCN314 FIFO, DP unblank, HDMI/DVI setup, DSC, and input-mode APIs.

## Important APIs, Types, and Macros
`SE_DCN314_REG_LIST(id)` is DCN30-like but removes `DP_DSC_BYTES_PER_PIXEL`, adds `DIG_FIFO_CTRL0`, and includes DP/HDMI/AFMT/DME register coverage. `SE_COMMON_MASK_SH_LIST_DCN314(mask_sh)` maps DP pixel-per-cycle processing, DP/HDMI packet fields, audio, DSC mode, metadata, `DIG_SYMCLK_FE_ON`, and FIFO output/read/enable/reset/done fields.

The prototypes expose constructor, shared DCN30 packet/audio helpers, `enc314_stream_encoder_dvi_set_stream_attribute`, `enc314_stream_encoder_hdmi_set_stream_attribute`, DP blank/unblank, FIFO reset/enable/disable, input mode, state readback, ODM combine, and DSC config.

## Control Flow and State
No executable flow lives in the header. It declares the hardware contract for the C implementation and for later DCN35 reuse. State is held in DP/DIG/HDMI/AFMT/DME registers.

## Dependencies and Integration Points
It includes VPG, AFMT, generic stream encoder, and DCN20 stream encoder headers. DCN35 includes this header to reuse FIFO, blank, read-state, DSC, and ODM functions.

## Risks and Test Signals
Risk comes from subtle field changes relative to DCN30, especially removed DSC bytes/slice registers and added FIFO control fields. Tests should cover build-time mask generation, FIFO enable/reset, DP unblank, HDMI info/audio packets, DSC mode readback, dynamic metadata, and DCN35 callers that reuse these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn314/dcn314_dio_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c

## Purpose
This file implements the DCN32 link encoder. It keeps most DCN30/DCN31 behavior but uses connector speed capability data, forces DP2 capability, queries USB-C alt-mode state through DMUB, and changes direct DP enable behavior when VBIOS execution is avoided.

## Important APIs and Functions
`enc32_hw_init` programs AUX DPHY RX/TX constants, sets `TMDS_CTL0`, and initializes AUX. `dcn32_link_encoder_enable_dp_output` delegates to the DCN10 VBIOS path unless `debug.avoid_vbios_exec_table` is true; in that direct-programming case the function intentionally does nothing. `query_dp_alt_from_dmub`, `dcn32_link_encoder_is_in_alt_mode`, and `dcn32_link_encoder_get_max_link_cap` use DMUB VBIOS transmitter query commands to derive DP Alt Mode and cap lanes to two when USB is active without DP4.

`dcn32_link_enc_funcs` reuses many DCN10/DCN20 operations, DCN31 DIO PHY mux, DCN32 alt/max-cap helpers, and `enc32_hw_init`. `dcn32_link_encoder_construct` initializes object state, maps transmitters A-E to DIG engines, queries `get_connector_speed_cap_info`, imports HBR/UHBR/HDMI capability bits, and sets `IS_DP2_CAPABLE = 1`.

## Control Flow
Construction is similar to DCN30 but capability data is connector-based instead of encoder-based. Alt-mode and max-link-cap queries always use DMUB; there is no non-DMUB legacy path in this file. DP enable returns early through VBIOS path unless direct programming is requested.

## State and Persistence
Persistent object state includes feature flags, connector identity, register pointers, preferred engine, and VBIOS-derived connector speed capabilities. Hardware state includes AUX DPHY registers, TMDS control, and any common link encoder state reached through delegated functions.

## Dependencies and Integration Points
The file depends on DCN31 DIO mux APIs, DMUB services, connector speed VBIOS callbacks, GPIO, link encoder base helpers, and debug flags. It is reused by DCN321 and DCN401 for selected behavior.

## Risks and Test Signals
Risks include direct DP enable becoming a no-op when VBIOS execution is avoided, mandatory DMUB availability for alt-mode queries, and connector-speed-cap callback absence or failure. Tests should cover VBIOS and direct DP enable modes, connector speed table parsing, USB-C lane limiting, DMUB query failure fallback, HBR/UHBR capability advertisement, and transmitter mapping for A-E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.h

## Purpose
This compact header declares the DCN32 link encoder public API. Unlike earlier generation headers, it does not add a large register-list macro; it reuses DCN30/DCN31 register contracts.

## Important APIs
The header declares `dcn32_link_encoder_construct`, `enc32_hw_init`, `dcn32_link_encoder_enable_dp_output`, `dcn32_link_encoder_is_in_alt_mode`, and `dcn32_link_encoder_get_max_link_cap`.

## Control Flow and State
Control flow is implemented in the C file. The APIs affect AUX init, DP output enable, object construction, and USB-C lane capability state. Persistent state is the underlying `dcn20_link_encoder`/`dcn10_link_encoder` object and hardware registers.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h` and is included by DCN321, DCN35, and DCN401 code that reuse DCN32 behavior or type declarations.

## Risks and Test Signals
The header risk is API drift: DCN321/DCN401 depend on these prototypes. Test signals include all dependent ASIC builds, DMUB alt-mode query linkage, DP output function-table binding, and constructor signature consistency with resource code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c

## Purpose
This file implements the DCN32 stream encoder, adapting the DCN30 stream path for newer DP pixel-per-cycle and FIFO behavior while retaining common DCN30 packet/audio support.

## Important APIs and Functions
`enc32_dp_set_odm_combine` writes `DP_PIXEL_PER_CYCLE_PROCESSING_MODE`. DVI/HDMI attribute setup mirrors DCN30 but notes that `DIG_START` is removed from the register spec and does not reset FIFO through that path. HDMI setup programs deep color, scrambling, general control, audio infoframe, and AVMUTE.

`enc32_stream_encoder_dp_unblank` computes DP M/N from timing and link rate, sets `DP_VID_N_MUL` and pixel-per-cycle mode for YCbCr420, DSC YCbCr422 non-simple, multiple OPPs, or `param->pix_per_cycle > 1`, disables DP stream, resets steer FIFO, waits for `DIG_SYMCLK_FE_ON`, programs FIFO read level, resets DIG FIFO with wait-for-done both ways, enables FIFO, delays, then enables DP video stream and traces source sequence.

`enc32_dp_set_dsc_config` only toggles DSC mode because bytes-per-pixel and slice-width registers were removed. `enc32_read_state` reads only remaining DSC/PPS state. `enc32_set_dig_input_mode`, `enc32_reset_fifo`, and `enc32_enable_fifo` manage DIG FIFO output pixel mode and reset/enable sequencing.

## Control Flow
The DCN32 function table keeps DCN30 packet/audio helpers, DCN2 DP stream attributes, and dynamic metadata, but overrides DP unblank, HDMI/DVI setup, DSC config/readback, input mode, and FIFO enable. There is no FIFO disable hook in the table.

## State and Persistence
Persistent state includes DP stream enable/status, DP VID M/N timing, DP pixel-per-cycle mode, DIG FIFO enable/reset/read-level/output mode, DSC mode, GSP11 PPS state, HDMI control registers, and AFMT audio state.

## Dependencies and Integration Points
Dependencies include DCN30 stream helper prototypes, `link_service` DP trace, `dpcd_defs`, VBIOS encoder control, `reg_helper`, and generic stream encoder contracts. Integration is via `struct stream_encoder_funcs` during DP/HDMI/DVI programming.

## Risks and Test Signals
Risks include FIFO wait timeouts if `DIG_SYMCLK_FE_ON` never asserts, wrong pixel-per-cycle handling for DSC/ODM/pix-per-cycle >1, and missing direct-programming FIFO reset in HDMI/DVI paths. Tests should cover DP unblank at standard and high pixel-per-cycle modes, DSC mode toggling, FIFO reset wait paths, HDMI scrambling/deep color, info packet reuse from DCN30, and DP trace sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h

## Purpose
This header defines the DCN32 stream encoder mask/shift surface and declares constructor plus FIFO/unblank helpers.

## Important APIs, Types, and Macros
`SE_COMMON_MASK_SH_LIST_DCN32(mask_sh)` maps DCN32 stream fields for DP pixel format and pixel-per-cycle mode, HDMI control/audio/generic-packet slots, DP secondary packets, DP M/N timing, metadata, DSC mode, Dolby Vision, `DIG_SYMCLK_FE_ON`, SDP splitting, clock pattern, and DIG FIFO control fields.

The public prototypes are `dcn32_dio_stream_encoder_construct`, `enc32_enable_fifo`, and `enc32_stream_encoder_dp_unblank`.

## Control Flow and State
No runtime flow is in the header. The macros drive generated register access used by the C file. The declared functions modify persistent DP/DIG/HDMI hardware register state.

## Dependencies and Integration Points
It includes DCN30 VPG/AFMT headers, `stream_encoder.h`, and DCN20 stream encoder helpers. DCN35 includes this header for reuse and compatibility.

## Risks and Test Signals
Risk is concentrated in field compatibility with the C implementation, especially FIFO and pixel-per-cycle fields. Test signals include compile coverage, DP unblank with FIFO enable, HDMI packet/audio programming, DSC mode readback, and dependent DCN35 build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c

## Purpose
This file implements the DCN321 link encoder variant. It combines DCN32 AUX/DP enable behavior with older DCN20 USB-C alt-mode/max-link helpers and connector-speed capability import.

## Important APIs and Functions
`dcn321_link_enc_funcs` uses `enc32_hw_init`, `dcn32_link_encoder_enable_dp_output`, DCN31 DIO PHY mux, common DCN10/DCN20 link operations, FEC hooks, and DCN20 alt-mode/max-link-cap functions. `dcn321_link_encoder_construct` initializes the base link encoder object and imports connector speed capability data from VBIOS.

## Control Flow
Construction sets USB-C feature state when the connector id is USB-C before copying `*enc_features`, then copies init fields, selects preferred engine for transmitters A-E, sets HDMI 6 Gb/s default true, queries `get_connector_speed_cap_info`, imports HBR2/HBR3/HDMI/UHBR flags, forces `IS_DP2_CAPABLE = 1`, and applies `debug.hdmi20_disable`.

## State and Persistence
Persistent state includes feature flags, connector and HPD metadata, transmitter/preferred DIG mapping, register and mask tables, and connector-speed capability bits. Runtime hardware state is handled by delegated DCN32/DCN20/DCN10 functions.

## Dependencies and Integration Points
It depends on DCN321 header, DCN31/32 link helpers, common link encoder contracts, VBIOS connector speed callbacks, and GPIO types. It integrates into resource construction for DCN321 ASICs.

## Risks and Test Signals
A notable risk is ordering: the USB-C `DP_IS_USB_C` bit is set before `enc10->base.features = *enc_features`, so the assignment may overwrite it unless `enc_features` already carries the bit. Tests should check USB-C feature propagation, DP Alt Mode behavior using DCN20 helpers, connector speed capability import, DP2/UHBR flags, HDMI disable override, and A-E transmitter mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.h

## Purpose
This header declares the DCN321 link encoder constructor and inherits the DCN32 link encoder contract.

## Important APIs
The single public API is `dcn321_link_encoder_construct`, taking the standard `dcn20_link_encoder`, initialization data, feature support, link/AUX/HPD register tables, and shift/mask tables.

## Control Flow and State
No control flow is defined here. The constructor declared here initializes persistent link encoder object state and VBIOS-derived capability state in the C implementation.

## Dependencies and Integration Points
It includes `dcn32/dcn32_dio_link_encoder.h`, which supplies the reused DCN32 declarations and base register expectations.

## Risks and Test Signals
Risk is low but API signature drift would break DCN321 resource construction. Test signals are compile/link coverage for DCN321 resources and runtime validation that the expected DCN321 function table is installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.c

## Purpose
This file implements the DCN35 link encoder, adding a newer DIG backend clock/mode model, fine-grain clock-gating control, unified link encoder assignment behavior, and explicit DPIA output APIs.

## Important APIs and Functions
`dcn35_is_dig_enabled` reads `DIG_BE_CLK_EN`; `dcn35_get_dig_mode` maps `DIG_BE_MODE` values to DP, DVI, HDMI, MST, or none. `dcn35_link_encoder_setup` writes `DIG_BE_MODE` for the requested signal and enables backend clocking. `dcn35_link_encoder_init` reuses `enc31_hw_init`. `dcn35_link_encoder_set_fgcg` toggles `DIO_FGCG_REP_DIS`.

The function table uses DCN35 setup, DIG state/mode functions, DCN31 USB-C alt/max-cap helpers, DCN31 DIO mux, and explicit `enable_dpia_output`/`disable_dpia_output`. Construction sets USB-C feature for USB-C connectors, imports connector speed capabilities, forces DP2 capable, maps transmitters A-E, and applies HDMI disable.

`dcn35_link_encoder_enable_dp_output`, `enable_dp_mst_output`, and `disable_output` choose between DCN31 mappable/DPIA behavior and older DCN20/DCN10 paths depending on `dc->config.unify_link_enc_assignment`. DPIA output helpers build DMUB DPIA control commands directly from caller-provided DPIA id, dig mode, and FEC readiness.

## Control Flow
Normal setup programs backend mode before enabling backend clock. DP enable/disable branches on unified assignment: non-unified uses DCN31 mappable support; unified directly calls legacy DP/MST disable/enable paths. DPIA enable configures encoder link settings, fills DMUB payload, and executes synchronously; disable skips if DIG is already off, then sends disable and clears training complete.

## State and Persistence
Persistent state includes DIG backend clock/mode, DIO fine-grain clock-gating, link encoder features, preferred engine, connector speed capabilities, DMUB-controlled DPIA state, and DP training-complete state. There is no software allocation.

## Dependencies and Integration Points
Dependencies include DCN31 link helpers, DCN35 header masks, DMUB service, connector speed VBIOS callbacks, link encoder base helpers, and the unified link encoder assignment configuration. It integrates with DP, MST, USB-C, DPIA, FEC, HPD, and HPO mux flows.

## Risks and Test Signals
Risks include using only clock enable as `is_dig_enabled`, potential USB-C feature overwrite if feature copy order is wrong, behavior differences under `unify_link_enc_assignment`, and DMUB DPIA command payload correctness. Tests should cover DIG mode readback for all signal types, backend clock enable, FGC gating toggle, unified/non-unified DP SST/MST paths, DPIA enable/disable payloads, connector speed capabilities, HDMI disable override, and USB-C lane limiting through DCN31 helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h

## Purpose
This header defines the DCN35 link encoder mask/shift surface and public API for new DIG backend clock/mode control, FGC gating, DP enable/disable, and DPIA output.

## Important APIs, Types, and Macros
`LINK_ENCODER_MASK_SH_LIST_DCN35(mask_sh)` maps DIG backend enable/control/clock fields, DP DPHY PRBS/symbol/scrambler/training fields, DP link/framing/stream/MST fields, AUX/HPD fields, FEC fields, DIO link HPO selection, and DIO clock gating fields. It is a large replacement-style mask list for the newer DCN35 backend register model.

Public APIs include constructor, init, `dcn35_link_encoder_set_fgcg`, `dcn35_is_dig_enabled`, `dcn35_get_dig_mode`, setup, DP SST/MST enable, output disable, and DPIA enable/disable.

## Control Flow and State
No executable flow is in the header. Declared functions modify DIG backend mode/clock, DP output state, DPIA state through DMUB, DIO clock gating, and link encoder object capabilities.

## Dependencies and Integration Points
The header includes DCN32, DCN30, and DCN31 link encoder headers, reflecting that DCN35 composes behavior from all three generations.

## Risks and Test Signals
Risk is high for mask drift because this header touches backend clocking, FEC, MST, AUX, HPD, HPO selection, and clock gating. Test signals include build coverage, DP/HDMI/DVI mode setup, HPD/AUX operation, FEC ready/active status, MST SAT programming, DIO FGC gating, and DPIA enable/disable through function-table hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.c

## Purpose
This file implements the DCN35 stream encoder, combining DCN314/32 stream behavior with a newer DIG frontend clock/enable model, stream-to-link mapping, HDMI TMDS format fields, and pixel-per-cycle readback.

## Important APIs and Functions
DVI setup mirrors DCN32 direct/VBIOS behavior. HDMI setup mirrors DCN30/314 but enables FIFO in direct mode, sets `TMDS_PIXEL_ENCODING` for YCbCr422, and clears `TMDS_COLOR_FORMAT`. `enc35_stream_encoder_enable` programs `DIG_FE_MODE` for DVI, HDMI, DP SST, DP MST, eDP, and virtual streams when enabling.

`enc35_stream_encoder_dp_unblank` computes DP M/N and pixel-per-cycle like DCN32, disables DP stream, resets steer FIFO, delays, enables DP stream, then calls `enc314_enable_fifo`. `enc35_stream_encoder_map_to_link` writes `DIG_STREAM_LINK_TARGET` in `STREAM_MAPPER_CONTROL`. `enc35_reset_fifo`, `enc35_enable_fifo`, `enc35_disable_fifo`, and `enc35_is_fifo_enabled` use `DIG_FE_CLK_CNTL`/`DIG_FE_EN_CNTL` and `DIG_FIFO_CTRL0`; FIFO enable turns on FE clock and FE enable before reset, while disable clears FIFO, FE enable, and FE clock. `enc35_get_pixels_per_cycle` maps FIFO output pixel mode to 1 or 2.

## Control Flow
The DCN35 function table reuses DCN314 ODM combine, blank, input mode, DSC config/readback, and DCN30 packet/audio helpers. It overrides HDMI/DVI setup, DP unblank, stream enable, FIFO hooks, stream-to-link mapping, and pixels-per-cycle query. Constructor is standard pointer assignment.

## State and Persistence
Persistent state includes DIG FE mode/clock/enable, FIFO reset/enable/read-level/output pixel mode, stream-to-link mapping, DP stream enable/status, DP VID M/N timing, HDMI TMDS encoding/color fields, DSC mode, packet state, and AFMT audio state.

## Dependencies and Integration Points
Dependencies include DCN30, DCN314, and DCN32 stream headers, `link_service`, `dpcd_defs`, VBIOS encoder control, AFMT/VPG helpers, and generic stream encoder function tables. Integration points include link mapping for decoupled stream/link encoders and DP trace sequencing.

## Risks and Test Signals
Risks include mixing `enc314_enable_fifo` in DP unblank while DCN35 has its own FE-clock-aware FIFO routine, stream-to-link assertion limits of `<5`, FE clock/enable sequencing, and HDMI YCbCr422 TMDS field changes. Tests should cover DP unblank and FIFO enable/disable, stream-to-link mapping for all valid instances, DP/HDMI/DVI frontend mode programming, pixels-per-cycle readback, HDMI YCbCr422, DSC, packet/audio reuse, and blank-time FIFO disable through DCN314 blank hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h

## Purpose
This header defines the DCN35 stream encoder register and mask/shift contract and exposes the DCN35 constructor plus FIFO control functions.

## Important APIs, Types, and Macros
`SE_DCN35_REG_LIST(id)` extends the DCN314-like DP/HDMI/AFMT/DME register set with `DIG_FE_EN_CNTL`, `DIG_FE_CLK_CNTL`, `DIG_FIFO_CTRL0`, and `STREAM_MAPPER_CONTROL`. `SE_COMMON_MASK_SH_LIST_DCN35(mask_sh)` maps DP pixel-per-cycle, HDMI control including TMDS pixel/color format fields, generic packet slots, DP secondary packets, metadata, DSC, DIG FE enable/mode/clock fields, FIFO fields, and stream mapper target.

The public APIs are `dcn35_dio_stream_encoder_construct`, shared DCN30 packet/audio helpers, `enc3_dp_set_dsc_pps_info_packet`, `enc35_disable_fifo`, and `enc35_enable_fifo`.

## Control Flow and State
The header defines no runtime flow. It provides the register/mask data needed by DCN35 stream functions to persist frontend clock, FIFO, stream mapping, HDMI, DP, packet, metadata, and audio state in hardware.

## Dependencies and Integration Points
It includes DCN30 VPG/AFMT, generic stream encoder, and DCN20 stream encoder headers. The implementation also relies on DCN314/32 helpers, so this header is part of a multi-generation composition.

## Risks and Test Signals
Risks include changed field locations for TMDS pixel/color format and Dolby Vision relative to earlier generations, plus new FE clock/enable and stream-mapper fields. Test signals include compile coverage, HDMI YCbCr422 field programming, FE clock/fifo enable behavior, stream mapping, DP unblank, metadata packets, and DSC PPS handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.c

## Purpose
This file implements the DCN401 link encoder. It resembles DCN32 capability and DMUB-alt-mode behavior while adopting a newer backend enable model like DCN35, including separate backend clock and enable bits.

## Important APIs and Functions
`enc401_hw_init` programs AUX DPHY constants, sets `TMDS_CTL0`, and initializes AUX. `dcn401_link_encoder_enable_dp_output` delegates to DCN10 VBIOS DP enable unless `debug.avoid_vbios_exec_table` is true; direct mode returns without programming. `dcn401_link_encoder_setup` writes `DIG_BE_MODE` for DP, DVI, HDMI, or MST, then sets both `DIG_BE_CLK_EN` and `DIG_BE_ENABLE`. `dcn401_is_dig_enabled` requires both bits. `dcn401_get_dig_mode` maps backend mode values back to signal types.

`dcn401_link_enc_funcs` uses DCN401 setup/state, DCN32 alt-mode and max-link-cap helpers, DCN31 DIO PHY mux, and common DCN10/DCN20 operations. `dcn401_link_encoder_construct` initializes object state, sets USB-C feature for USB-C connectors, maps transmitters A-E, queries connector speed capabilities, forces DP2 capable, imports HBR/UHBR/HDMI flags, and applies HDMI disable.

## Control Flow
Construction is connector-capability based. Setup is signal-driven and always enables backend clock and backend logic after mode selection. DP enable has the same VBIOS/direct split as DCN32. Alt-mode and max-link-cap behavior are delegated to DCN32 DMUB query helpers.

## State and Persistence
Persistent state includes backend mode, backend clock enable, backend enable, AUX DPHY registers, TMDS control, feature flags, preferred engine, connector speed capability bits, USB-C feature state, and common DP/HDMI link registers through delegated helpers.

## Dependencies and Integration Points
Dependencies include DCN31 DIO mux, DCN32 alt/max-cap helpers, DCN30 register contracts, VBIOS connector speed callback, GPIO, and common link encoder functions. It integrates into DCN401 resource construction and link programming paths.

## Risks and Test Signals
Risks include direct DP enable no-op under `avoid_vbios_exec_table`, mandatory DMUB availability through DCN32 alt helpers, duplicate `MIN` definition guards, USB-C feature copy ordering, and consistency between backend clock/enable state and disable paths delegated to older code. Tests should cover backend mode/setup for DP/DVI/HDMI/MST, `is_dig_enabled` with both bits, connector speed capability import, USB-C lane limiting, DP enable under both debug modes, HDMI disable override, and transmitter mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.h

## Purpose
This header defines the DCN401 link encoder mask/shift surface and public constructor/setup/state APIs. It is a newer-generation backend register contract similar to DCN35 but with a smaller exported API.

## Important APIs, Types, and Macros
`LINK_ENCODER_MASK_SH_LIST_DCN401(mask_sh)` maps DIG backend enable/control/clock fields, DP DPHY PRBS/symbol/scrambler/training fields, DP link/framing/stream/MST fields, AUX and HPD fields, and FEC state. It provides the fields used by DCN401 setup, state readback, AUX init, and inherited link operations.

The header declares `dcn401_link_encoder_construct`, `enc401_hw_init`, `dcn401_link_encoder_enable_dp_output`, `dcn401_link_encoder_setup`, `dcn401_get_dig_mode`, and `dcn401_is_dig_enabled`. `dcn401_get_dig_mode` is declared twice, which is harmless in C but noisy.

## Control Flow and State
No executable flow is present. Declared functions program backend clock/enable/mode, AUX DPHY, DP output, and object feature state in the C implementation.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h` and the C implementation composes DCN31 and DCN32 behavior. Resource construction and link function-table setup depend on this signature.

## Risks and Test Signals
Risks include mask drift for backend enable/clock fields, duplicate prototype maintenance, and missing fields compared with DCN35 if shared code expands. Test signals include compile coverage, backend mode setup, DP/HDMI/DVI/MST operation, FEC status, HPD/AUX operation, and DCN32 USB-C alt-mode integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.h -->
