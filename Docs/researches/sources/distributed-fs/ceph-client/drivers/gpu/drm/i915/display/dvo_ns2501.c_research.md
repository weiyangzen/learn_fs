# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/dvo_ns2501.c

Purpose: i915 DVO driver for National Semiconductor NS2501 panel controller, with reverse-engineered mode tables for 1024x768 laptop panels.

Important APIs/functions: exported `ns2501_ops` implements init, detect, mode_valid, mode_set, dpms, get_hw_state, and destroy. The file defines register constants, mode-specific configuration tables for 640x480, 800x600, and 1024x768, mode-agnostic register values, and I2C read/write helpers.

Control flow: init allocates private state and probes vendor/device low bytes. Mode validation accepts exactly three mode/clock combinations. Mode set writes init registers, mode-agnostic register table, then mode-specific PLL, scaler, sync, display-window, position, dither, and sync-control values, storing the selected config in private state. DPMS uses the stored config to sequence output/backlight enable or disable with fixed delays.

State and persistence: `struct ns2501_priv` stores quiet flag and pointer to the current configuration. Hardware state persists in NS2501 registers. DPMS assumes `mode_set()` has already populated `ns->conf`.

Dependencies and integration points: i915 DVO core, I2C, DRM debug logging, and DVO connector/encoder machinery.

Risks: the driver relies on reverse-engineered magic values and only supports three exact modes. `detect()` always returns connected due to unreliable hardware detection. Calling DPMS before mode_set could dereference a null config. I2C write failures are ignored during large table programming.

Test signals: vendor/device probe, exact supported mode validation, visible output for all three tabled modes, DPMS/backlight sequence, behavior after suspend/resume, and missing-device I2C failure handling.
