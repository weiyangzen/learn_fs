# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.h

Purpose: declares the vendor fixed VS/PE retimer training interface.

Important APIs: `dp_perform_fixed_vs_pe_training_sequence` runs the special training sequence; `dp_fixed_vs_pe_set_retimer_lane_settings` packs requested DPCD lane settings into retimer VS/PE vendor commands; `dp_fixed_vs_pe_read_lane_adjust` converts retimer query bytes into per-lane `dpcd_training_lane` adjustments.

Control flow/state: callers supply initialized `link_training_settings`; this header itself stores no state. The implementation uses common DP training result enums and lane-count constants.

Dependencies/integration: includes `link_dp_training.h` and is consumed by DP training selector code and any PHY path that must talk to the fixed retimer.

Risks: exported helpers expose vendor-specific behavior through generic-looking lane structures, so callers must ensure the hardware really is this retimer before using them.

Test signals: build coverage on configurations with retimer support and hardware tests verifying helper packing/unpacking matches actual retimer registers.
