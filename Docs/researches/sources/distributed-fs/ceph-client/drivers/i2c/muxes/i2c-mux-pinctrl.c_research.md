# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pinctrl.c

Purpose: Platform I2C mux selected by pinctrl states. It is for systems where channel selection is achieved by changing pin muxing rather than programming a mux chip.

Important APIs/types/functions: `struct i2c_mux_pinctrl` holds the pinctrl handle and flexible state array. `i2c_mux_pinctrl_select()` selects a channel state. `i2c_mux_pinctrl_deselect()` selects a final `"idle"` state when present. `i2c_mux_pinctrl_root_adapter()` walks pinctrl settings to infer mux-lock safety. Probe resolves `i2c-parent`, obtains pinctrl states, allocates an `i2c_mux_core`, and adds adapters.

Control flow: Probe counts `pinctrl-names`, gets the parent adapter, allocates mux state, looks up each named state, treats a last state named `"idle"` as deselect-only, determines `mux_locked`, and creates child adapters for non-idle states. Selection is a direct `pinctrl_select_state()` call. Removal deletes adapters and releases the parent adapter.

State and persistence: The driver stores only pinctrl state pointers and mux core data. Active hardware state is held by the pinctrl provider until another channel or idle state is selected.

Dependencies/integration: OF `i2c-parent`, `pinctrl-names`, pinctrl consumer APIs, internal pinctrl core setting structures, I2C adapter lookup, and I2C mux core.

Risks: The file includes pinctrl internal headers, so core layout changes can break it. `"idle"` must be last. Wrong root-adapter inference changes mux locking behavior. Parent adapter lookup may defer probe.

Test signals: Valid DT creates one adapter per non-idle state. Non-last `"idle"` fails. Same-root states should log mux-locked; mixed roots should not. Transfers should visibly select the expected pinctrl state and idle state.
