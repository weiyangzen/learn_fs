# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.c

Purpose: manages eDP panel mode, backlight control, panel power sequencing, ILR optimization, PSR, Panel Replay, ALPM, ASSR, and related firmware context programming.

Important APIs/functions: panel mode is handled by `dp_get_panel_mode`/`dp_set_panel_mode`; AUX/nits backlight by `edp_set_backlight_level_nits`, `edp_get_backlight_level_nits`, `edp_backlight_enable_aux`, and `set_default_brightness_aux`; PWM/ABM backlight by `edp_set_backlight_level`, `edp_get_backlight_level`, and `edp_get_target_backlight_pwm`; power/timing by `edp_panel_backlight_power_on`, `edp_set_panel_power`, `edp_wait_for_t12`, `edp_receiver_ready_T9`, and `edp_receiver_ready_T7`; PSR by `edp_setup_psr`, `edp_set_psr_allow_active`, `edp_get_psr_state`, `edp_get_psr_residency`, and `edp_set_sink_vtotal_in_psr_active`; Replay by `edp_setup_freesync_replay`, `edp_set_replay_allow_active`, `edp_get_replay_state`, `edp_send_replay_cmd`, `edp_set_coasting_vtotal`, and residency/power helpers.

Control flow: mode selection checks external encoder branch IDs/names for special converter behavior before using eDP DPCD caps. Backlight paths choose VESA AUX, AMD AUX, OLED defaults, ABM, panel controller, or firmware depending on caps and control type. Power sequencing orders VDD, HPD wait, backlight, and RX power according to eDP direction. PSR setup clears sink config, fills DPCD PSR bits, enables ALPM/vtotal control when supported, builds a `psr_context` from stream/timing/link/ASIC state, then copies settings into DMUB PSR or DMCU. Replay follows a similar pattern with replay DPCD config, ALPM, and DMUB replay context.

State/persistence: updates `link->panel_mode`, `link->psr_settings`, `link->replay_settings`, `link->panel_cntl->stored_backlight_registers`, and DPCD registers. It reads `dc->current_state` pipe mappings and persistent debug/config/caps flags.

Dependencies/integration: uses `link_dpcd`, `link_dp_capability`, `dm_helpers`, ASIC IDs, `link_dp_phy`, DMUB PSR/Replay services, `abm`, resource helpers, and panel replay helpers. It crosses HWSS, DMCU, DMUB, ABM, panel controller, PSP, and current resource state boundaries.

Risks: many functions return success after partial behavior for DDS or unsupported paths. DPCD helper truthiness is easy to misread because `DC_OK` is zero. PSR/Replay setup is sensitive to panel instance lookup, stream timing, firmware availability, and ASIC-specific workarounds. Power sequencing delays are panel-specific and failures can cause blanking or hangs.

Test signals: eDP panel power-on/off sequencing, AUX and PWM backlight on OLED/non-OLED panels, ILR optimization decisions with BIOS-programmed rates, PSR v1/v2 enable/state/residency, FreeSync Replay/ALPM configuration, ASSR via PSP/DMUB, HPD-ready waits, and suspend/resume with stored backlight state.
