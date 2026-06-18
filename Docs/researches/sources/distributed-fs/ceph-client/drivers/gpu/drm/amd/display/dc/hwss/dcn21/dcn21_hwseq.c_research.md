# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.c

## Purpose
Implements DCN 2.1-specific system aperture setup, power-state clock transitions, Renoir/S0i3 workarounds, HDMI/DP PLL workaround, and ABM/backlight control through DMUB or legacy DMCU.

## Important APIs, Types, and Functions
Exports `dcn21_init_sys_ctx`, `dcn21_s0i3_golden_init_wa`, `dcn21_exit_optimized_pwr_state`, `dcn21_optimize_pwr_state`, `dcn21_PLAT_58856_wa`, `dcn21_dmub_abm_set_pipe`, `dcn21_set_abm_immediate_disable`, `dcn21_set_pipe`, `dcn21_set_backlight_level`, and `dcn21_is_abm_supported`. The private `mmhub_update_page_table_config` reads VM context page-table base registers. Important types include `struct dcn_hubbub_phys_addr_config`, `struct dc_phy_addr_space_config`, `union dmub_rb_cmd`, `struct abm`, `struct panel_cntl`, and `struct set_backlight_level_params`.

## Control Flow
System-context init copies firmware/KMD aperture and GART fields, patches page-table base from VM context registers, then calls Hubbub `init_dchub_sys_ctx`. Power optimize/exit delegates to `clk_mgr->update_clocks` with optimized flag true/false. The PLAT_58856 workaround temporarily clears `dpms_off`, toggles DPMS on/off through link service, then restores `dpms_off`. ABM setup builds DMUB ABM commands when DMCU is absent; otherwise it falls back to DCE110 DMCU hooks. Backlight programming sets ABM pipe normal mode and then sends PWM/frame-ramp data either through ABM function pointers or a raw DMUB command.

## State and Persistence Behavior
Mutates Hubbub system aperture programming, clock manager state, stream `dpms_off`, panel stored backlight level, and DMUB command queue state. The ABM support predicate reads pipe topology and rejects ODM-combined streams.

## Dependencies and Integration Points
Depends on DMUB service (`dc_wake_and_execute_dmub_cmd`), `clk_mgr`, `dccg`, `hubbub`, ABM, DMCU, panel control, and link service. Integrated by `dcn21_init.c` and inherited by later DCN30/DCN31 init tables for backlight and optimized power hooks.

## Risks and Test Signals
Risks include stale page-table base register reads, DMUB command payload mismatch, backlight ramp stalls, DMCU/DMUB path divergence, and the PLAT_58856 workaround toggling DPMS in unexpected stream states. Test with Renoir S0i3, monitor-off HDMI hotplug/unplug, modern standby, ABM enable/disable, DMCU-present and DMCU-absent panels, and ODM streams where ABM should be unsupported.
