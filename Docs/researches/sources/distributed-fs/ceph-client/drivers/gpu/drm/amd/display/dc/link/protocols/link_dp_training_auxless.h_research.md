# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.h

Purpose: declares the AUX-less link-training entry point.

Important API: `dp_perform_link_training_skip_aux(struct dc_link *, const struct link_resource *, const struct dc_link_settings *)` returns a boolean success value after hardware-only training.

Control flow/state: the header does not define state; it relies on `link_dp_training.h` structures and common DP training configuration.

Dependencies/integration: included by code that wants to bypass normal AUX/DPCD status exchange. It is not a replacement for standard DP training when sink feedback is available.

Risks: the boolean API cannot expose detailed link-training failure classes, and the implementation reports success unconditionally once hardware programming completes.

Test signals: build coverage for selector code, plus platform tests proving this path is not accidentally used for normal DP/eDP links.
