# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c

Purpose: Implements DCN301 panel power/backlight control using direct PWM and power-sequencer registers.

Important APIs/types/functions: `dcn301_panel_cntl_construct()` initializes the panel controller function table. Static handlers implement `hw_init`, destroy, backlight-on query, power-on query, backlight register store, and current-backlight calculation. `dcn301_get_16_bit_backlight_from_pwm()` converts PWM period/count/fractional state into a 16-bit backlight value.

Control flow: Hardware init reads `BL_ACTIVE_INT_FRAC_CNT`. If BIOS left invalid values `0` or `1`, it restores cached PWM registers or writes fallback defaults. Otherwise it caches current PWM registers and reference divider. It enables PWM output, unlocks group 1 registers, computes the current backlight, and returns it. State queries read `PANEL_BLON`, `PANEL_PWRSEQ_TARGET_STATE_R`, `PANEL_DIGON`, and `PANEL_DIGON_OVRD`.

State/persistence: Persistent software state lives in `panel_cntl->stored_backlight_registers`. Hardware state is PWM control, period, reference divider, group lock, and power-sequencer bits.

Dependencies/integration: Depends on `panel_cntl`, `dce_panel_cntl` register definitions, DC register helpers, and kernel `kfree`. It provides `struct panel_cntl_funcs` to higher display code.

Risks: Backlight math uses bit shifts based on `BL_PWM_PERIOD_BITCNT`; invalid or unexpected bit counts could overflow masks. Fallback constants are hardware-specific. Register writes occur without an explicit DMUB mediation layer, unlike DCN31.

Test signals: Validate BIOS-bug recovery, cache/store/restore behavior, PWM-to-16-bit conversion with fractional and non-fractional modes, and power/backlight query bits.
