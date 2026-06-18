# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c

Purpose: implements LCD/eDP-specific ABM hardware initialization and DMUB commands for adaptive backlight, PWM fractional mode, configuration upload, pause/save/restore, pipe selection, backlight level, and event control.

Important functions: `dmub_abm_init()` initializes ABM sampling, histogram, IPS CSC coefficient selection, PWM current/target/user levels, min/max thresholds, missed-frame clears, and fractional PWM. Command emitters include `dmub_abm_set_level()`, `dmub_abm_init_config()`, `dmub_abm_set_pause()`, `dmub_abm_save_restore()`, `dmub_abm_set_pipe()`, `dmub_abm_set_backlight_level()`, and `dmub_abm_set_event()`.

Control flow: register init uses `REG_WRITE`, `REG_SET_*`, and `REG_UPDATE` on DCE ABM/PWM registers, then sends `DMUB_CMD__ABM_SET_PWM_FRAC` with a panel mask covering current eDP count. Command helpers zero a `union dmub_rb_cmd`, populate type/subtype/version/payload fields, set panel masks or instances, and execute synchronously through `dc_wake_and_execute_dmub_cmd()`. Config and save/restore use DMUB scratch framebuffer memory: flush, copy CPU data to scratch, pass GPU address and byte count to firmware, then copy scratch back for save/restore.

State and persistence: backlight and ABM levels persist in hardware registers and firmware state. `dmub_abm_save_restore()` uses caller-provided `struct abm_save_restore` as a persistence exchange buffer. Scratch memory contents are transient but shared with DMUB firmware.

Dependencies and integration: depends on `dce_abm` register descriptors, DMUB command definitions, `dc_dmub_srv`, scratch memory framebuffer, DC config flags such as `disable_fractional_pwm`, and panel/eDP count in `dc_context`.

Risks: no explicit size validation before copying config/save data into scratch memory is visible here. Several functions always return true after issuing a synchronous command, so command failure propagation depends on lower layers. `dmub_abm_set_pause()` writes payload size through `cmd.abm_set_level.header`, which aliases the union but is fragile. Test signals include scratch-buffer bounds, command payload bytes for each subtype, fractional PWM panel masks, save/restore round trips, and backlight u16.16 values across multiple panels.
