<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h -->
# sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h

Purpose: Defines platform data for Samsung matrix keypad controllers.

Important APIs/types/functions: `SAMSUNG_MAX_ROWS` and `SAMSUNG_MAX_COLS` set 8x8 limits. `struct samsung_keypad_platdata` carries matrix keymap data, row/column counts, autorepeat disable flag, wakeup capability, and optional GPIO configuration callback.

Control flow: Probe configures GPIOs, builds keymap, sets input repeat/wakeup behavior, and scans rows/cols.

State/persistence: Platform data persists for the controller lifetime; wakeup and GPIO settings persist across power states.

Dependencies/integration: Depends on generic matrix keypad helpers and input key reporting.

Risks: GPIO callback must match row/col counts; wakeup settings affect suspend behavior.

Test signals: 8x8 boundary keymaps, no-autorepeat behavior, wake-from-suspend, and GPIO setup invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h -->
