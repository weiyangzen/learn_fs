## sources/distributed-fs/ceph-client/drivers/input/keyboard/maple_keyb.c

Purpose: Sega Dreamcast Maple bus keyboard driver. It polls keyboard condition packets and maps USB-HID-like scancodes to Linux input events.

Important APIs/types/functions: `struct dc_kbd` stores input, a 256-entry keycode table, and old/new 8-byte report buffers. `dc_scan_kbd()` reports modifier bits and key-array changes. `dc_kbd_callback()` receives Maple queue completions. `probe_maple_kbd()` registers input and installs `maple_getcond_callback()`.

Control flow: probe allocates state, copies keymap, registers input, requests Maple condition polling at approximately VBLANK cadence, and stores driver data. Callback validates the function word, copies the report, and scans changes under a cleanup mutex. Removal locks the mutex, unregisters input, frees state, and clears driver data.

State/dependencies/integration: state is the two keyboard report buffers. It depends on Maple bus condition polling, input core, a global cleanup mutex, and manually allocated devices.

Risks and test signals: modifier keys are reported every scan, which is acceptable but noisy. In the non-modifier press path, the code reports a press only when the new code is found in the old report; this looks inverted for new key detection and should be regression-tested carefully. Test single key press/release, six-key rollover changes, callback during removal, unknown scancodes, and Maple function mismatch.
