# sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.c

Purpose: board database and board-specific GPIO/power/LED/LNA behavior for Siano SMS1xxx devices.

Important APIs/functions: exported `sms_get_board()` returns static board metadata; `sms_board_setup()` applies initial GPIO states; `sms_board_power()` handles power-state GPIO effects; `sms_board_led_feedback()` updates LEDs while caching LED state via core API; `sms_board_lna_control()` toggles LNA/RF switch GPIOs; `sms_board_load_modules()` requests `smsdvb`; `sms_board_event()` is a currently mostly-empty event hook.

Control flow: board IDs index `sms_boards[]`, whose entries define name, device type, firmware per mode, default mode, interface number, MTU, crystal, remote map, LED/LNA/RF GPIOs, and GPIO config fields. GPIO helper handles negative pin numbers as inverted GPIOs.

State/persistence: static board table is read-only metadata; LED state is stored via `smscore_led_state()`; actual state is hardware GPIO level. No durable persistence.

Dependencies/integration: depends on `smscoreapi` for board IDs/GPIO operations and on `smsir`/RC maps for IR metadata. Called by Siano USB/SDIO/core/DVB code during hotplug, mode setup, tuning, and feedback.

Risks/test signals: `sms_get_board()` uses `BUG_ON` for invalid IDs, making caller validation critical. Some board fields are `-1`/0 sentinel pins. Tests should cover every board ID, inverted GPIO behavior, LNA unsupported returns, LED duplicate suppression, firmware name selection, and module auto-load.
