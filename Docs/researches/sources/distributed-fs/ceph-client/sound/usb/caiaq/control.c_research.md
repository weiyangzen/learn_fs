# sources/distributed-fs/ceph-client/sound/usb/caiaq/control.c

## Purpose
Creates per-product ALSA HWDEP controls for CAIAQ/Native Instruments LEDs, input modes, ground lift, software lock, and controller illumination state.

## Important APIs, Types, and Functions
Public function is `snd_usb_caiaq_control_init()`. Core callbacks are `control_info()`, `control_get()`, and `control_put()` using a shared `kcontrol_template`. `struct caiaq_controller` maps control names to indexes, with many static per-product tables such as `ak1_controller`, `rk2_controller`, `rk3_controller`, `kore_controller`, `a8dj_controller`, `kontrolx1_controller`, `kontrols4_controller`, and `maschine_controller`.

## Control Flow
`snd_usb_caiaq_control_init()` selects a control table by USB id and calls `add_controls()`. Each control uses `private_value` either as a bit position into `control_state` or as a byte index flagged by `CNT_INTVAL`. `control_info()` exposes boolean or bounded integer ranges, with product-specific max values. `control_put()` updates the cached byte/bit, sends the changed `control_state` to the device using EP1 commands, endpoint 8 for Traktor Kontrol S4 integer controls, or banked LED dimming for Maschine, and rolls back cache on USB error.

## State and Persistence
The persistent state is `cdev->control_state[256]` plus `ep8_out_buf`. It represents current software-visible control/LED settings and is initialized partly by `device.c` for Audio 8 DJ.

## Dependencies and Integration Points
Depends on `device.c` command helpers and product ids in `device.h`. The controls are added after `snd_card_register()` in `setup_card()`, so they become part of the ALSA card interface.

## Risks
`kcontrol_template` is a mutable static modified during `add_controls()`; registration is serialized by probe context, but static mutation is fragile. Control state writes can send all 256 bytes for many simple changes. Bounds are based on table correctness; out-of-range private indexes would access `control_state`. Product-specific endpoint 8 path must match descriptors.

## Test Signals
Enumerate controls for each supported product id, write every control boundary value, inject USB command failure to verify rollback, and test Maschine bank split and S4 endpoint 8 writes.
