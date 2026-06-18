# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.c

Purpose: provides a deliberately minimal DP link-training path that skips AUX validation and only programs source hardware timing/patterns before returning success.

Important API: `dp_perform_link_training_skip_aux` computes normal training settings with `dp_decide_training_settings`, applies preferred overrides, programs the CR training pattern/lane settings, waits the CR interval, programs the EQ pattern/lane settings, waits the EQ interval, switches to video mode, logs success, and returns `true`.

Control flow: there are no DPCD link-setting writes, lane-status reads, sink adjustment requests, or failure classification. The function is linear and assumes the configured link will lock without feedback.

State/persistence: uses stack-local `link_training_settings`; applies `link->preferred_training_settings` as overrides. Hardware state is changed through `dp_set_hw_training_pattern`, `dp_set_hw_lane_settings`, and `dp_set_hw_test_pattern`.

Dependencies/integration: includes `link_dp_training_auxless.h` and `link_dp_phy.h`; it still relies on common DP training setting selection.

Risks: always reporting success can hide bad cables, wrong rates, disconnected sinks, or lane-setting mismatch. It is only appropriate for paths where AUX is intentionally unavailable or already bypassed by platform policy.

Test signals: verify callers only select this path for valid AUX-less scenarios, confirm video pattern is restored, and use hardware/link-status observation outside this function to catch failures.
