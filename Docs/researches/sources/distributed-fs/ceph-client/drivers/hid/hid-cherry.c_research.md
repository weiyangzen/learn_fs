# sources/distributed-fs/ceph-client/drivers/hid/hid-cherry.c

Purpose: handles Cherry Cymotion special keyboards by fixing an invalid report descriptor and mapping three nonstandard consumer usages to programmable key codes.

Important APIs/types/functions: `ch_report_fixup()` checks descriptor bytes around offsets 11/12 and rewrites two usage/logical range pairs to `0x03ff`, allowing parsing of the broken Cymotion descriptor. `ch_input_mapping()` maps consumer usages `0x301`, `0x302`, and `0x303` to `KEY_PROG1`, `KEY_PROG2`, and `KEY_PROG3`. `ch_devices[]` matches the wired and solar Cymotion IDs. `ch_driver` registers report fixup and input mapping only.

Control flow: HID core calls the descriptor fixup before parsing. During HID input setup, consumer usages matching the three Cherry special keys are consumed and mapped; all other usages fall through to generic HID input mapping.

State/persistence: no private state is allocated. The descriptor mutation is per parse and the key mappings become part of the input device capabilities.

Dependencies/integration: uses HID report fixup and `hid_map_usage_clear()` integration with hid-input. It depends on Cherry IDs from `hid-ids.h` and standard input key codes.

Risks: offset-based descriptor mutation assumes the known broken descriptor layout. The key mapping only handles three usages; additional model-specific special keys may still be unmapped or generic. Because there is no probe callback, failures are surfaced by generic HID probe paths.

Test signals: parse both Cymotion device IDs, confirm the fixup log and successful input device creation, press the three special keys and observe `KEY_PROG1..3`, and verify unrelated consumer/media keys still work through generic mapping.
