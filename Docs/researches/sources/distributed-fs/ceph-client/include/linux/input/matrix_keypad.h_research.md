<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h -->
# sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h

Purpose: Provides generic helpers and encoding for matrix keypad keymaps.

Important APIs/types/functions: `MATRIX_MAX_ROWS/COLS`, `KEY(row,col,val)`, `KEY_ROW()`, `KEY_COL()`, `KEY_VAL()`, and `MATRIX_SCAN_CODE()` encode/decode matrix positions. `struct matrix_keymap_data` stores an encoded keymap array. `matrix_keypad_build_keymap()` builds an input keymap and capabilities; `matrix_keypad_parse_properties()` reads rows/cols from firmware/device properties.

Control flow: Keypad drivers parse firmware or platform keymap during probe, then convert row/col scan results to keycodes.

State/persistence: The built keymap persists in the input device; source map may be static platform data.

Dependencies/integration: Depends on input devices, firmware properties, and key code UAPI.

Risks: Row/column limits are 32 each; row_shift must match scanner encoding or keys map incorrectly.

Test signals: Keymap build from platform and firmware, boundary rows/cols, duplicate/invalid entries, and scan-to-key event tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h -->
