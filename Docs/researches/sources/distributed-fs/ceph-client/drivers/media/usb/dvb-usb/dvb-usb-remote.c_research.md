# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-remote.c

Purpose: remote-control support for the DVB USB library. It supports both old legacy input-device polling and newer rc-core devices, plus a helper for decoding NEC-like five-byte firmware key buffers.

Important APIs/functions: `dvb_usb_remote_init()` and `dvb_usb_remote_exit()` are exported lifecycle helpers. Legacy paths include keymap get/set functions, `legacy_dvb_usb_read_remote_control()`, and `legacy_dvb_usb_remote_init()`. Rc-core paths include `dvb_usb_read_remote_control()` and `rc_core_dvb_usb_remote_init()`. `dvb_usb_nec_rc_key_to_event()` decodes legacy NEC buffers.

Control flow: init returns if RC polling is disabled or no RC properties are present. Legacy mode allocates `input_dev`, populates key bits, registers it, initializes delayed work, and periodically calls driver `rc_query()` to emit press/repeat/release events. Rc-core mode allocates `rc_dev`, sets map/protocol fields, registers it, and either lets bulk mode handle events elsewhere or schedules delayed polling. Exit cancels delayed work and unregisters/free devices based on mode.

State and persistence: device state tracks `input_dev` or `rc_dev`, `rc_phys`, last event/state, work item, and `DVB_USB_STATE_REMOTE`. Keymaps are static property tables, but legacy `setkeycode` can mutate keycodes in place at runtime.

Dependencies and integration: depends on Linux input, rc-core, USB input ID helpers, and each board driver's RC query callback/protocol fields.

Risks: `legacy_dvb_usb_setkeycode()` writes `keymap->keycode` instead of `keymap[index].keycode`, so remapping can update the first entry rather than the selected one. Poll callbacks contain TODOs about locking and can skip rescheduling if polling is disabled while running. Rc-core bulk mode relies on device-specific URB completion outside this file.

Test signals: legacy and rc-core device creation, keymap get/set, delayed polling interval clamping, NEC checksum/repeat decoding, RC5/NEC maps from board properties, bulk-mode devices, disable_rc_polling module parameter, and disconnect while work is pending.
