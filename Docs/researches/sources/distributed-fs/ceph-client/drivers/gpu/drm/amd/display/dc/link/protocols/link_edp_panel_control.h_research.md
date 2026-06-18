# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.h

Purpose: declares the eDP panel-control surface for link code and display core.

Important APIs: exposes panel mode, AUX/PWM backlight, PSR, Replay, ILR optimization, ALPM, power sequencing, receiver readiness, SmartMux support, and ASSR programming functions. Notable signatures include `edp_setup_psr`, `edp_setup_freesync_replay`, `edp_set_psr_allow_active`, `edp_set_replay_allow_active`, and `edp_set_panel_power`.

Control flow/state: the header groups functions that mutate `dc_link` panel, PSR, Replay, backlight, and DPCD state. Callers must provide valid stream/pipe context for PSR/Replay and hardware backlight operations.

Dependencies/integration: includes `link_service.h`, which supplies `dc_link`, stream, timing, and panel-related type visibility. Implementations integrate with HWSS, DPCD, ABM, DMCU/DMUB, and PSP.

Risks: this is a broad API with many feature-specific booleans; callers must understand whether a `true` return means feature configured, no-op success, or unsupported-but-not-fatal behavior.

Test signals: compile coverage from DC link, PSR, Replay, and backlight callers; runtime panel feature probes for every exported path.
