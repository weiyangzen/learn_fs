# sources/distributed-fs/ceph-client/drivers/media/rc/xbox_remote.c

Purpose: USB scancode rc-core driver for original Xbox DVD Movie Playback Kit IR dongles from Microsoft and Gamester. It reads interrupt reports and emits `RC_PROTO_XBOX_DVD` scancodes through rc-core.

Important APIs and functions: `struct xbox_remote` stores rc device, USB device/interface, interrupt URB, input buffer, and name/path strings. Key functions are `xbox_remote_rc_open`, `xbox_remote_rc_close`, `xbox_remote_input_report`, `xbox_remote_irq_in`, `xbox_remote_rc_init`, `xbox_remote_initialize`, probe, and disconnect.

Control flow: probe validates a single interrupt IN endpoint, allocates state, scancode rc device, buffer, and URB, builds device name/path, sets default keymap `RC_MAP_XBOX_DVD`, initializes rc fields, fills the interrupt URB, and registers rc-core. The URB is submitted on rc device open and killed on close. Completion validates six-byte reports, extracts a little-endian 16-bit key code from bytes 2-3, calls `rc_keydown`, and resubmits the URB.

State and persistence: per-device USB and rc state lives until disconnect. Last-key/repeat timing is handled by rc-core using a 10 ms timeout. No persistent storage exists.

Dependencies and integration points: depends on USB interrupt APIs, USB input ID helpers, rc-core scancode mode, protocol `RC_PROTO_XBOX_DVD`, and keymap `RC_MAP_XBOX_DVD`.

Risks and edge cases: the report validation uses `urb->actual_length != 6 || urb->actual_length != data[1]`, so any mismatch logs and drops input. There is no suspend/resume handler; open URBs rely on USB core disconnect/reset behavior. Unaligned cast to `__le16 *` on `data + 2` is typically safe on supported architectures but less robust than `get_unaligned_le16`. A zero-endpoint alternate interface is silently ignored.

Test signals: USB probe for both vendor/product IDs, open/close URB submission, six-byte report decoding, keymap events, repeat/keyup timing with 10 ms timeout, unplug while opened, malformed report logging, and behavior across USB reset/suspend.
