# sources/distributed-fs/ceph-client/drivers/input/keyboard/cros_ec_keyb.c

## Purpose

`cros_ec_keyb.c` is the ChromeOS Embedded Controller keyboard driver. It consumes EC MKBP events for matrix keys, non-matrix buttons, switches, and sysrq, performs host-side deghosting and Fn-layer mapping, and registers one or two input devices.

## Important APIs, Types, and Functions

- `struct cros_ec_keyb` stores matrix geometry, ghost filter state, old matrix state, EC pointer, matrix and button/switch input devices, notifier, Vivaldi physmap, and Fn-layer state.
- `cros_ec_keyb_work()` is the EC event notifier for matrix, sysrq, button, and switch events.
- `cros_ec_keyb_process()` diffs matrix columns, applies optional ghost filtering, and emits changed keys.
- `cros_ec_keyb_process_key_fn_map()` implements a second keymap layer when `KEY_FN` and Fn mappings are present.
- `cros_ec_keyb_info()`, `cros_ec_keyb_register_bs()`, and `cros_ec_keyb_query_switches()` query EC-supported/current buttons and switches.
- `cros_ec_keyb_register_matrix()` parses matrix properties, builds normal plus Fn-layer keymap rows, computes valid keys, parses Vivaldi metadata, and registers input.

## Control Flow

Probe waits for a fully registered parent EC, allocates state, optionally registers the matrix keyboard, registers supported non-matrix buttons/switches, then registers a blocking notifier on the EC event chain and enables wakeup. Matrix events wake the device, validate event length against column count, then diff and report changed keys. Button/switch events are translated from EC bitmaps to `EV_KEY`/`EV_SW`. Sysrq events are forwarded to `handle_sysrq()`. Resume requeries switch state because switch events may be lost during suspend.

## State and Persistence Behavior

`old_kb_state` persists previous EC matrix bytes for edge detection. `valid_keys` persists the subset used by ghost filtering. Fn state tracks whether Fn is down and whether it was used in a combo so standalone Fn can be emitted only on release. Button/switch supported masks are not stored after registration; current switch state is queried on resume.

## Dependencies and Integration Points

The driver integrates with ChromeOS EC command/protocol APIs, EC event notifier chain, input core, matrix keypad helpers, Vivaldi function-row helpers, sysrq, ACPI match `GOOG0007`, OF compatibles `google,cros-ec-keyb` and `google,cros-ec-keyb-switches`, and firmware properties such as `keypad,num-rows`, `keypad,num-columns`, `linux,keymap`, `google,needs-ghost-filter`, and `function-row-physmap`.

## Risks and Edge Cases

Matrix columns are limited by EC protocol to 18. The ghost filter drops an entire matrix state when it detects ghosting, which can delay unrelated key changes. Fn-layer release logic depends on current input keybits, so keymap changes and dropped states must stay consistent. Buttons/switches-only ACPI/OF matches expect EC support and fail otherwise. Event-size mismatches are discarded.

## Test Signals

Test matrix events at valid and invalid lengths, ghosting combinations, Fn-only and Fn-combo behavior, runtime setkeycode changes, Vivaldi sysfs visibility, button/switch support masks, switch resume queries, sysrq forwarding, wakeup behavior during suspend, and deferred probe when the EC is not registered.
