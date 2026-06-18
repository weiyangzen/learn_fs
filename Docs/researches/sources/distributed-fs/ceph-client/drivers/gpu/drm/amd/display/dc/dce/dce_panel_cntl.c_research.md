# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.c

## Purpose
This file implements DCE panel control for embedded-panel power/backlight state. It reads and restores PWM registers, takes backlight ownership from BIOS, enables PWM output, reports panel backlight/power state, stores backlight registers, and programs new PWM duty cycles.

## Important APIs and Functions
The vtable `dce_link_panel_cntl_funcs` supplies `destroy`, `hw_init`, `is_panel_backlight_on`, `is_panel_powered_on`, `store_backlight_level`, `driver_set_backlight`, and `get_current_backlight`. `dce_panel_cntl_construct()` initializes the object. Internal helpers include `dce_get_16_bit_backlight_from_pwm()`, `dce_panel_cntl_hw_init()`, `dce_is_panel_backlight_on()`, `dce_is_panel_powered_on()`, `dce_store_backlight_level()`, and `dce_driver_set_backlight()`.

## Control Flow
Hardware init restores cached PWM registers when available, otherwise caches BIOS-initialized values if they look valid, otherwise programs fallback PWM defaults. It then sets `ATOM_S2_VRI_BRIGHT_ENABLE` in `BIOS_SCRATCH_2`, enables `BL_PWM_EN`, unlocks group registers, and returns the current 16-bit backlight computed from PWM period and duty cycle. Backlight setting locks group registers, computes a 16-bit active duty cycle from a U16.16 brightness input and the masked period, writes `BL_ACTIVE_INT_FRAC_CNT`, unlocks, and waits for the update-pending bit to clear.

## State and Persistence
Persistent software state is mostly `panel_cntl->stored_backlight_registers`, containing PWM control, PWM period, and PWM reference divider values across init/store cycles. Hardware state persists in LVTMA power-sequence registers, PWM registers, group lock/update bits, and BIOS scratch ownership bits.

## Dependencies and Integration Points
The file depends on `reg_helper.h`, `core_types.h`, `dc_dmub_srv.h`, `panel_cntl.h`, `dce_panel_cntl.h`, and `atom.h`. It integrates with embedded panel initialization, BIOS scratch ownership conventions, and higher-level DC backlight control.

## Risks and Test Signals
Brightness math depends on `BL_PWM_PERIOD_BITCNT`; invalid zero or very small bit counts can affect masks and shifts. Fallback PWM defaults assume VBIOS should normally initialize registers. Writes to BIOS scratch and PWM ownership can conflict with firmware expectations if ordering changes. Test signals include resume/backlight restore, brightness ramp tests, fractional and integer PWM modes, panel power/backlight state reads, and update-pending timeout behavior.
