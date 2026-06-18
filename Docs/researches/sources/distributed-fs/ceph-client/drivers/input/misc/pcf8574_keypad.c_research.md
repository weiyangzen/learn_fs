# sources/distributed-fs/ceph-client/drivers/input/misc/pcf8574_keypad.c

Purpose: I2C input driver for a 4x4 keypad attached to a PCF8574 I/O expander.

Important APIs/types/functions: SMBus byte access, threaded IRQ, input keymap, and PM ops. `struct kp_data` stores keymap, input, client, names, and `laststate`. Main routines are `read_state`, IRQ handler, probe, remove, suspend, and resume.

Control flow: probe writes an initial byte to verify the expander, allocates state/input, copies static keymap, sets EV_KEY bits, initializes state with `read_state`, requests low-triggered threaded IRQ, registers input, and stores client data. `read_state` drives nibbles and reads active-low row/column state to compute a button index. IRQ compares new state with `laststate`, reports press for in-range state or release of previous key, syncs, and updates state. Suspend disables IRQ; resume enables it.

State/persistence: `laststate` is RAM-only and assumes one key at a time.

Dependencies/integration: I2C ID `pcf8574_keypad`, fixed keymap, input EV_KEY.

Risks: SMBus errors in `read_state` are unchecked. Multiple simultaneous keys are not represented. Probe checks zeroed destination keymap before assignment, relying on allocation semantics. IRQ suspend ignores wake needs.

Test signals: all 16 keys, release/no-key state, multi-key ambiguity, SMBus failures, IRQ suspend/resume, keymap exposure, and cleanup paths.
