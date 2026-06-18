## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb-leds.c

Purpose: this optional companion adds Linux LED class support for RTL8366RB per-port LED groups. It parses `leds` child nodes under DSA port nodes, maps each LED group's manual-control bit in the RTL8366RB LED registers, and registers binary LED class devices with blocking brightness setters.

Important APIs, types, and functions: `rtl8366rb_setup_leds()` iterates DSA ports and their LED child nodes. `rtl8366rb_setup_led()` parses each LED node's `reg` LED group, initializes a `struct rtl8366rb_led`, applies `default-state`, and calls `devm_led_classdev_register_ext()`. `rb8366rb_set_port_led()` updates group/port bits and switches the group mode to `RTL8366RB_LEDGROUP_FORCE` through `rb8366rb_set_ledgroup_mode()`. `rb8366rb_get_port_led()` reads the manual LED state.

Control flow: setup skips ports with no DT node or no `leds` child. For each child LED, `reg` selects one of four LED groups; invalid groups fail setup. Default state `on` or `off` immediately writes the manual state, while `keep` reads the current bit. The registered brightness callback writes manual on/off state and ensures the group is in force mode, because the manual state registers are ignored when a hardware trigger mode is selected.

State and persistence: software state lives in `struct rtl8366rb_led leds[port][group]` embedded in the chip private structure when `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS` is enabled. Hardware state is split between group trigger mode in `RTL8366RB_LED_CTRL_REG` and per-port manual bits in `RTL8366RB_LED_0_1_CTRL_REG` or `RTL8366RB_LED_2_3_CTRL_REG`. Device-managed LED registration handles cleanup.

Dependencies and integration points: this file depends on `rtl8366rb.h`, the parent Realtek regmap, DSA port device nodes, firmware node LED properties, and the LED classdev API. The parent `rtl8366rb_setup()` calls `rtl8366rb_setup_leds()` unless LEDs are disabled globally by DT; with the Kconfig option disabled, the header supplies a no-op.

Risks: switching any LED in a group to manual force mode changes the trigger mode for the entire group across ports, which can disable hardware activity/speed indication unexpectedly. `kasprintf()` allocates `init_data.devicename` without an explicit free in this function. Errors from applying default state are not checked before registration. The debug/error messages sometimes print group and port values in a confusing order.

Test signals: DT LED nodes with `reg` 0 through 3 should create named LED class devices, invalid `reg` should warn and fail, default-state `on`/`off`/`keep` should match hardware bits, brightness writes should update the corresponding manual register bits, and using a manual LED should set its group mode to `RTL8366RB_LEDGROUP_FORCE`.
