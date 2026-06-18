<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h -->
# sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h

Purpose: Provides sparse keymap support for devices whose scancodes are not dense matrix/table indices.

Important APIs/types/functions: Entry types include key, fixed switch, variable switch, ignored entry, and terminator. `struct key_entry` maps device-specific code to keycode or switch code/value. APIs find entries by scancode or keycode, set up a sparse keymap with optional per-entry setup, report a specific entry, and report by scancode with optional autorelease.

Control flow: Drivers install a sparse keymap at probe, then report events by hardware code; helpers translate and emit input events.

State/persistence: Keymap entries are attached to the input device keycode storage for its lifetime.

Dependencies/integration: Depends on input key/switch UAPI and input device keycode mechanisms.

Risks: Ignored and variable switch entries need deliberate handling to avoid false events.

Test signals: Lookup by scancode/keycode, autorelease keys, fixed and variable switches, ignored entries, and setup callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h -->
