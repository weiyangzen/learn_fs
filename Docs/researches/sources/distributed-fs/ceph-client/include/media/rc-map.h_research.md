# sources/distributed-fs/ceph-client/include/media/rc-map.h

## Purpose
Defines remote-controller protocol bitmasks, scancode construction macros, keymap structures, keymap registration APIs, and the canonical names of in-kernel keymaps.

## Important APIs, Types, and Functions
Macros map `enum rc_proto` values to `RC_PROTO_BIT_*` masks and build aggregate encoder/decoder masks based on enabled Kconfig decoders. Scancode helpers cover NEC, NECX, NEC32, RC5, RC5_SZ, RC6_0, and RC6_6A. `struct rc_map_table`, `struct rc_map`, and `struct rc_map_list` define scancode/keycode tables. APIs are `rc_map_register()`, `rc_map_unregister()`, and `rc_map_get()`. Many `RC_MAP_*` string constants name built-in keytables.

## Control Flow
RC drivers set a default map name or register maps; rc-core looks up maps by name and translates scancodes into Linux input keycodes.

## State and Persistence Behavior
Registered `rc_map_list` entries persist globally while modules are loaded. Individual `rc_map` entries carry spinlock-protected table state and protocol identity.

## Dependencies and Integration Points
Depends on input keycodes and LIRC protocol UAPI. Integrates rc-core with individual keymap modules and media drivers that select default remotes.

## Risks
Keymap names are string ABI within the kernel/module ecosystem; typos break autoload/default selection. Aggregate protocol masks depend on Kconfig and must not advertise unavailable decoders.

## Test Signals
Keymap module registration/unregistration, default map lookup by every referenced name, protocol mask exposure for enabled/disabled decoders, scancode macro tests, and sorted-name maintenance.
