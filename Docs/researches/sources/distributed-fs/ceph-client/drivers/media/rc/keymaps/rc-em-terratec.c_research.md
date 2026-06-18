# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/rc-em-terratec.c

## Purpose

`rc-em-terratec.c` provides the `RC_MAP_EM_TERRATEC` remote-controller keymap for `em-terratec remote controller keytable`. It is a data-only rc-core map: decoded remote-control scan codes are translated into Linux input `KEY_*` events for the bundled receiver or board driver. The table has 28 scan-code entries; early entries include `0x01->KEY_CHANNEL`, `0x02->KEY_SELECT`, `0x03->KEY_MUTE`, `0x04->KEY_POWER`, `0x05->KEY_NUMERIC_1`, `0x06->KEY_NUMERIC_2`. The represented controls cover numeric entry, power/input selection, navigation/menu, channel/volume, DVR/media transport.

## Important APIs, Types, and Functions

- `struct rc_map_table em_terratec[]` is the static scan-code-to-keycode table.
- `struct rc_map_list em_terratec_map` publishes `.scan = em_terratec`, `.size = ARRAY_SIZE(em_terratec)`, `.rc_proto = RC_PROTO_UNKNOWN`, and `.name = RC_MAP_EM_TERRATEC` to rc-core.
- The module init function calls `rc_map_register()` and the exit function calls `rc_map_unregister()`, so the map is visible to rc-core only while the object is built in or the module is loaded.
- It has normal `module_init()`/`module_exit()` hooks.

## Control Flow

There is no active decode algorithm in this file. At build or module-load time, the map is registered with the rc-core map registry. A receiver driver later sets an `rc_dev->map_name` matching `RC_MAP_EM_TERRATEC` or userspace selects that map with tooling such as `ir-keytable`; rc-core then looks up decoded scancodes in `em_terratec` and emits the associated input keycodes. Unload or rc-core teardown unregisters the map, after which new lookups by name should fail or fall back to another configured map.

## State and Persistence Behavior

The persistent state is the compiled static table plus the registry node in rc-core. The file does not allocate per-device memory, take locks, touch hardware, or persist user settings. Runtime key state, repeat filtering, protocol decoding, and user remaps live in rc-core, the receiver driver, and input/ir-keytable configuration rather than in this keymap source.

## Dependencies and Integration Points

The file depends on `media/rc-map.h`, `linux/module.h`, Linux input `KEY_*` definitions, the `RC_MAP_*` string namespace, and the protocol enum `RC_PROTO_UNKNOWN`. It is built through `drivers/media/rc/keymaps/Makefile` when `CONFIG_RC_MAP` is enabled, except for CEC-style integration if noted above. Board, USB, PCI, CEC, or platform IR drivers integrate with it by naming `RC_MAP_EM_TERRATEC` as their default map.

## Risks and Edge Cases

Incorrect scancodes, wrong `KEY_*` assignments, a mismatched `.rc_proto`, or a stale `.name` break user-visible remote buttons without producing compile errors. Because the protocol is `RC_PROTO_UNKNOWN`, correctness depends on the consuming hardware driver or legacy decoder path supplying matching scancodes. Table ordering is not semantically important for lookups, but duplicate or vendor-overloaded scancodes should be reviewed carefully. The map can also drift from the v4l-utils userspace copy, causing different behavior between built-in maps and maps loaded from userspace.

## Test Signals

Useful checks include compiling the keymap with `CONFIG_RC_MAP=y` and `=m`, loading/unloading the generated module where applicable, confirming `rc_map_register()` exposes `RC_MAP_EM_TERRATEC`, using `ir-keytable -r` or equivalent rc-core introspection to inspect the map, and pressing representative numeric, navigation, volume/channel, power, and media keys on the target remote. Protocol-specific tests should verify that decoded `RC_PROTO_UNKNOWN` scancodes match the table values and that unknown buttons do not alias to unsafe actions such as power or record.
