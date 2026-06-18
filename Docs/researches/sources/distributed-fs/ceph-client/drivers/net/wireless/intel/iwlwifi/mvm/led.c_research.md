# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/led.c

## Purpose

`led.c` registers and controls the iwlwifi MVM radio LED class device. It maps Linux LED brightness changes to either a firmware LED command on newer firmware or direct CSR register writes on older hardware, and synchronizes LED state after firmware startup.

## Important APIs, Types, And Functions

- `iwl_mvm_leds_init()` validates the module LED mode, allocates the LED name, initializes `mvm->led`, registers the class device, and sets `IWL_MVM_INIT_STATUS_LEDS_INIT_COMPLETE`.
- `iwl_led_brightness_set()` is the LED class callback and translates brightness to boolean on/off.
- `iwl_mvm_led_set()` selects firmware command control when `IWL_UCODE_TLV_CAPA_LED_CMD_SUPPORT` exists, otherwise writes `CSR_LED_REG`.
- `iwl_mvm_send_led_fw_cmd()` sends asynchronous `LEDS_CMD` only when firmware is running.
- `iwl_mvm_leds_sync()` reapplies brightness after firmware startup for firmware-controlled LEDs.
- `iwl_mvm_leds_exit()` unregisters and frees LED state.

## Control Flow

Initialization accepts default and RF-state modes, rejects unsupported modes, and treats blink mode as unsupported before falling back to RF-state behavior. Runtime brightness changes call the class callback, which calls the MVM LED setter. Firmware-controlled LEDs send an async command; register-controlled LEDs write directly. Sync is skipped if LEDs were not registered or if pre-8000 hardware uses direct register control.

## State And Persistence

State is limited to `mvm->led`, the dynamically allocated LED name, current LED brightness maintained by the LED subsystem, and `mvm->init_status`. There is no persistence; LED state is reissued after firmware startup when needed.

## Dependencies And Integration Points

The file depends on the Linux LED class subsystem, `iwlwifi_mod_params.led_mode`, mac80211 radio LED trigger names, firmware LED command definitions, CSR register access, firmware-running status, and MVM init status flags. `iwl_mvm_up()` calls `iwl_mvm_leds_sync()` near the end of firmware bring-up.

## Risks And Edge Cases

- Firmware LED commands are skipped when firmware is down, so sync after startup is necessary for command-controlled devices.
- Blink mode is explicitly unsupported, which may surprise users setting `led_mode=blink`.
- If LED registration fails, the allocated name must be freed; this file handles that path.
- Direct CSR LED writes are hardware-family sensitive and intentionally avoided for newer firmware-command devices.

## Test Signals

Validation includes LED class device registration under `/sys/class/leds`, RF-state trigger behavior, manual brightness toggles, firmware restart followed by LED sync, `led_mode=disable` producing no device, invalid LED mode returning `-EINVAL`, and absence of `LED command failed` warnings on firmware-controlled hardware.
