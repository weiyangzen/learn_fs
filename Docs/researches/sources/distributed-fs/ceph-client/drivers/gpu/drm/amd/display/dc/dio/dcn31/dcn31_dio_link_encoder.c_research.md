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
