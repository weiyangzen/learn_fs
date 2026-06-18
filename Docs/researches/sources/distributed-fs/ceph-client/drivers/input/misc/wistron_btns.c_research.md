# sources/distributed-fs/ceph-client/drivers/input/misc/wistron_btns.c

## Purpose
`wistron_btns.c` supports legacy Wistron/Acer/Fujitsu/Medion laptop hotkeys and LEDs through a BIOS call interface. It selects a DMI/keymap, maps BIOS memory, polls a BIOS event queue, reports sparse-keymap input events, and optionally controls Wi-Fi, Bluetooth, mail, and Wi-Fi LEDs through BIOS calls.

## Important APIs, Types, and Functions
BIOS access is built around `struct regs`, `call_bios()`, `map_bios()`, `bios_pop_queue()`, `bios_attach()`, `bios_detach()`, `bios_get_cmos_address()`, `bios_get_default_setting()`, and `bios_set_state()`. DMI/keymap selection uses many `struct key_entry` arrays, `dmi_matched()`, `select_keymap()`, and `copy_keymap()`. Runtime input flow uses `handle_key()`, `poll_bios()`, `wistron_poll()`, and `setup_input_dev()`. LED integration uses `led_classdev` callbacks and PM hooks.

## Control Flow
Module init selects a keymap from module parameter or DMI, copies it out of init memory, maps BIOS code/data, registers a platform driver, and creates a platform device. Probe attaches to BIOS, gets the CMOS queue-length address, initializes Wi-Fi/Bluetooth state from BIOS defaults, registers LEDs when present, and sets up a polled input device. Polling reads queue length from CMOS, repeatedly pops BIOS queue entries, and handles key codes unless flushing. Key handling toggles BIOS Wi-Fi/Bluetooth state for special entries or reports sparse-keymap events. Suspend disables radios and suspends LEDs; resume restores saved radio state, resumes LEDs, and flushes stale BIOS events.

## State and Persistence Behavior
Global state includes BIOS mapping pointers, selected keymap, platform device, input device, CMOS queue address, radio availability/enabled flags, LED presence, and last keypress jiffies. BIOS radio/LED state is persistent platform firmware state. Poll interval changes dynamically between 500 ms idle and 100 ms burst after recent keys.

## Dependencies and Integration Points
The driver is x86 BIOS-specific and depends on DMI, sparse-keymap, input polling, LED class, CMOS RTC access, ioremap, inline x86 assembly, platform devices, and preemption/IRQ control. It integrates with userspace through an input device and LED class devices `wistron:green:mail` and `wistron:red:wifi`.

## Risks and Edge Cases
Calling firmware through inline assembly with interrupts disabled is inherently fragile and architecture-specific. BIOS signature detection and mapping can match unsupported systems; `force=1` can load with an empty keymap only for discovery. DMI tables are large and legacy; wrong matches can toggle radios or LEDs incorrectly. BIOS queue polling uses CMOS length and firmware pop calls without locking against firmware. LED and radio toggles are stateful BIOS side effects, and suspend powers radios off even if userspace expected them to remain active.

## Test Signals
Test known DMI matches, `keymap=` overrides, `force=1`, BIOS signature absence, queue polling and unknown key logging, sparse-keymap event delivery, Wi-Fi/Bluetooth toggle behavior, LED registration and brightness callbacks, suspend/resume radio restoration, and safe module unload unmapping BIOS resources.
