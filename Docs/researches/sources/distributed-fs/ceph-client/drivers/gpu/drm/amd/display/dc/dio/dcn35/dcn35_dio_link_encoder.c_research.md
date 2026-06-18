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
