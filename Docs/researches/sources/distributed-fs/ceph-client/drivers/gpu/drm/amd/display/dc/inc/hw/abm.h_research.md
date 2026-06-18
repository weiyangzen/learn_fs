# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/abm.h

## Purpose

`abm.h` defines the Ambient Backlight Management hardware/firmware abstraction. It provides callbacks for ABM initialization, level control, pipe binding, PWM backlight programming, pause, configuration loading, and save/restore.

## Important APIs, Types, And Functions

`struct abm` stores context, vtable, and whether DMCU is running. `struct abm_funcs` includes `abm_init`, `set_abm_level`, `set_abm_immediate_disable`, `set_pipe`, `set_backlight_level_pwm`, `get_current_backlight`, `get_target_backlight`, `init_abm_config`, `set_abm_pause`, `save_restore`, and `set_pipe_ex`.

## Control Flow

Display code initializes ABM with current backlight/user level, assigns an OTG/controller and panel instance, loads optional firmware/config data, then changes ABM level or PWM ramp on user/power events. Disable and pause paths stop ABM effects immediately or temporarily for panel/pipe transitions.

## State And Persistence Behavior

The ABM object persists in the resource pool or per-pipe ABM arrays. Firmware/hardware holds current and target backlight state; save/restore preserves panel-specific ABM data through transitions. No on-disk persistence exists.

## Dependencies And Integration Points

It includes `dm_services_types.h` and integrates with HWSS backlight/ABM callbacks, DMCU/DMUB firmware, panel control, eDP paths, and stream resources in `core_types.h`.

## Risks And Edge Cases

Panel instance, OTG/controller ID, and power-sequence instance must match the active stream. ABM calls may depend on DMCU/DMUB firmware running. PWM values use U16.16 fixed-point semantics where 1.0 is max backlight. Save/restore data is opaque and implementation-specific.

## Test Signals

Tests should cover ABM init, level changes, immediate disable, pause/resume, backlight PWM ramps, pipe rebinding, suspend/resume save/restore, and firmware-not-running fallbacks. Visible backlight jumps or stale dimming are key runtime signals.
