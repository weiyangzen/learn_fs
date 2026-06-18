# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/led.h

Purpose: Defines the firmware LED switching command payload.

Important APIs and types: `struct iwl_led_cmd` contains one little-endian `status` field indicating LED on/off state for `LEDS_CMD`.

Control flow: No executable flow. LED control code sends this command when the driver wants firmware to update LED state.

State and persistence: Header owns no state. Firmware applies LED state until the next command, device reset, or platform LED policy override.

Dependencies and integration points: Used by the legacy `LEDS_CMD` command ID and DVM/MVM LED handling paths.

Risks: The command is intentionally tiny; incorrect endian conversion or command version selection is the main hazard. Platform or rfkill LED policy can make expected visual state differ from firmware command state.

Test signals: LED on/off command submission, endian correctness, firmware command version compatibility, rfkill/suspend interactions, and absence of LED hardware.
