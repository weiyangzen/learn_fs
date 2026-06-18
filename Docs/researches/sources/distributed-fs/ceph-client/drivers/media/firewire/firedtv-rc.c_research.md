# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-rc.c

Purpose: Adds optional Linux input support for FireDTV remote-control notifications. It registers an input device, supplies keymaps for current and older remotes, and translates AV/C remote codes into key press/release events.

Important APIs/types/functions: `oldtable` maps older 0x4501..0x451f and 0x4540..0x4542 codes. `keytable` maps 2008-era 0x0300..0x031f and 0x0340..0x0354 codes. `fdtv_register_rc()` allocates and registers `input_dev`, copies the mutable keytable to `idev->keycode`, and sets supported key bits. `fdtv_unregister_rc()` cancels remote work, frees keycode storage, and unregisters input. `fdtv_handle_rc()` maps a received vendor code to a key and emits press/release syncs.

Control flow: FireWire probe registers RC before adding the node to FCP routing. `avc_recv()` handles remote-control changed notifications, calls `fdtv_handle_rc()`, and schedules work to re-register for notify events. Remove cancels that work via unregister. Invalid codes are logged and ignored.

State and persistence: Runtime state is the input device pointer and copied keycode table in `fdtv->remote_ctrl_dev`. Keymaps are not persisted beyond input core runtime configuration.

Dependencies/integration: Depends on Linux input subsystem, workqueues, and `firedtv.h`. Compiled only when `CONFIG_DVB_FIREDTV_INPUT`; otherwise header stubs make callers no-ops.

Risks and test signals: Test allocation failures, input registration failure unwind, keymap mutability via input core, all supported code ranges, invalid code logging, work cancellation during remove, and disabled-input builds. `fdtv_unregister_rc()` assumes registration succeeded and `remote_ctrl_dev` is valid, so caller ordering and failure paths need coverage.
