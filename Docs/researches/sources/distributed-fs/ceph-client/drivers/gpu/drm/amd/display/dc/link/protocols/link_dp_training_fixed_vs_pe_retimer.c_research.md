# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.c

Purpose: isolates the non-standard 8b/10b link-training sequence required by a vendor fixed VS/PE embedded retimer. It wraps standard DP training with retimer-specific DDC/AUX commands, lane-setting interception, and link-rate workarounds.

Important APIs/functions: `dp_perform_fixed_vs_pe_training_sequence` is the main entry; `dp_fixed_vs_pe_set_retimer_lane_settings` forces retimer VS/PE values; `dp_fixed_vs_pe_read_lane_adjust` queries retimer-reported DPRX lane adjustments. A private non-transparent path reuses standard `perform_8b_10b_*` phases after retimer setup.

Control flow: non-transparent LTTPR mode uses the common 8b/10b sequence with a minimum 16 ms CR interval and optional link-rate toggle before writing the real rate. Transparent/no-LTTPR mode resets retimer lane settings, enables intercept, writes spread/lane/rate DPCD, optionally toggles link rate when no LTTPR IEEE OUI is present, applies vendor DPMF and four-lane commands, disables intercept during first CR retry, then runs custom CR and EQ loops with retimer VS/PE updates before DPCD lane writes.

State/persistence: updates `link->vendor_specific_lttpr_link_rate_wa`, mutates `lt_settings`, and programs retimer state through `link_configure_fixed_vs_pe_retimer`/`link_query_fixed_vs_pe_retimer` on `link->ddc`. It writes normal DP DPCD fields through `core_link_write_dpcd` and shared training helpers.

Dependencies/integration: depends on `link_dp_training_8b_10b`, `link_dpcd`, `link_dp_phy`, `link_dp_capability`, and `link_ddc`. It is selected for specific retimer hardware while preserving common result enums.

Risks: magic vendor payloads, intercept toggling, delay tuning, and rate toggles are hardware-specific. AUX/DDC command failures are not always checked uniformly. Incorrect lane-count packing can misprogram per-lane settings.

Test signals: target retimer platforms with 1/2/4 lanes, no-OUI and OUI-present LTTPR caps, non-transparent mode, debug `fixed_vs_aux_delay_config_wa`, CR max retry, EQ failure classification, and retimer readback of DPRX requested VS/PE.
