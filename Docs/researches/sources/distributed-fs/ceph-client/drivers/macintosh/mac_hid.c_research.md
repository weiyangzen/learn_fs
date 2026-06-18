# sources/distributed-fs/ceph-client/drivers/macintosh/mac_hid.c

Purpose: implements legacy Macintosh mouse button 2/3 emulation by converting configurable keyboard keycodes into middle/right mouse button input events. It exposes sysctls under `/proc/sys/dev/mac_hid`.

Important APIs and functions: `mac_hid_create_emumouse()` allocates/registers a synthetic `input_dev`; `mac_hid_emumouse_filter()` intercepts matching `EV_KEY` events and reports `BTN_MIDDLE` or `BTN_RIGHT`; `mac_hid_emumouse_connect()` attaches an `input_handle` to all key-capable devices except the synthetic device itself; `mac_hid_toggle_emumouse()` is the sysctl handler that starts/stops emulation atomically. `mac_hid_files` defines `mouse_button_emulation`, `mouse_button2_keycode`, and `mouse_button3_keycode`.

Control flow: module init registers the sysctl table. When userspace writes `1` to `mouse_button_emulation`, the driver creates the synthetic mouse and registers an input handler. The handler opens matching devices and filters configured keycodes into mouse events. Writing `0` unregisters the handler and synthetic device. Module exit unregisters sysctls and stops active emulation.

State and persistence: global sysctl-backed integers hold enable state and keycodes. Runtime state is `mac_hid_emumouse_dev`, protected by `mac_hid_emumouse_mutex` during enable/disable. Settings are not persistent across reboot.

Dependencies and integration: integrates with the input subsystem, sysctl/proc handlers, ADB bus identity for the synthetic device, and lockdep class annotation for the created device.

Risks: keycode sysctls can be changed while emulation is running without locking against event filtering. The filter consumes configured keys for all key-capable input devices. Error recovery in the toggle handler restores the old enable value, but partial input handler/device failures must remain paired.

Test signals: sysctl registration, enabling/disabling repeatedly, no self-binding loop, key-to-button event generation, invalid enable values returning `-EINVAL`, and module unload while enabled.
