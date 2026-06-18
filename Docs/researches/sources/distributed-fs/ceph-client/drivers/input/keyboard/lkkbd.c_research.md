## sources/distributed-fs/ceph-client/drivers/input/keyboard/lkkbd.c

Purpose: DEC LK201/LK401 serial keyboard driver for serio RS232 adapters. It supports key events, LED updates, bell, keyclick, Ctrl-click, reset/ID handling, and LK401 extended mode.

Important APIs/types/functions: `struct lkkbd` stores keycode table, ignored ID bytes, input device, serio port, reinit work, names, type, and volume settings. `lkkbd_interrupt()` handles incoming bytes; `lkkbd_reinit()` sends reset/default/mode/audio/LED commands; `lkkbd_event()` handles `EV_LED` and `EV_SND`; `lkkbd_connect()`/`lkkbd_disconnect()` bind the serio device.

Control flow: connect allocates state, copies the keymap, opens serio, registers input, and sends a power-cycle reset. Initial response bytes are collected into `id`; after six bytes `lkkbd_detection_done()` names the keyboard and reports self-test/stuck-key results. Runtime key bytes toggle their current state because LK up/down mode sends one byte per transition. `LK_ALL_KEYS_UP` releases all mapped keys. A `0x01` reset response starts another ID collection and schedules reinitialization work.

State/dependencies/integration: runtime state lives in `ignore_bytes`, ID bytes, input LED/sound bits, and hardware mode programmed over serio. Integration is via `module_serio_driver`, input event callbacks, workqueue, and module parameters for volumes/layout behavior.

Risks and test signals: key state toggling depends on correct keyboard mode; missed bytes can invert state until `LK_ALL_KEYS_UP`. Work and interrupt paths share serio writes without deep protocol locking. Test reset/ID sequences, LK201 compose-as-alt parameter, LED/sound event writes, all-keys-up recovery, disconnect while work is pending, and unknown scancode logging.
