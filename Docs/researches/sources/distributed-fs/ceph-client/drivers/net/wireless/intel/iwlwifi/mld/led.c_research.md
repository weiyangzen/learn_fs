# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.c

Purpose: Registers and drives the optional Linux LED class device for MLD hardware, translating brightness changes into firmware `LEDS_CMD` commands.

Important APIs/types/functions: `iwl_mld_leds_init()`, `iwl_mld_led_config_fw()`, `iwl_mld_leds_exit()`, `iwl_led_brightness_set()`, and `iwl_mld_send_led_fw_cmd()`.

Control flow: Initialization reads `iwlwifi_mod_params.led_mode`, accepts default/RF-state mode, rejects unsupported values, and maps blink to RF-state with an error. It allocates a LED name, sets a brightness callback, optionally uses the mac80211 radio LED trigger, and registers with the LED class. Brightness changes send async firmware LED commands only when firmware is running. Firmware reconfiguration replays current brightness after firmware start.

State/persistence: Stores the LED class device in `mld->led`, including allocated `led.name`, default trigger, current brightness, and max brightness. Exit unregisters and frees the name, then nulls it.

Dependencies/integration: Depends on Linux LED class, mac80211 radio LED trigger, MLD firmware command helpers, module LED mode parameters, and the firmware long-group LED command.

Risks: LED commands are async, so payload lifetime relies on transport command-copy semantics. Firmware command attempts before `fw_status.running` are warned/rejected. Unsupported blink mode is silently downgraded after logging, which may surprise users expecting blink behavior.

Test signals: Build configurations with and without `CONFIG_IWLWIFI_LEDS` should compile. Runtime checks include LED registration success, brightness toggles producing firmware commands only while running, replay after firmware restart, and clean unregister/free on op-mode stop.
