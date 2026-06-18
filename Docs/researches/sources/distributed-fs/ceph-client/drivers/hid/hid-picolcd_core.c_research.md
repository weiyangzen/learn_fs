<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_core.c

## Purpose
This is the central PicoLCD HID driver. It owns probe/remove, raw report dispatch, synchronous command/response handling, keypad input, operation-mode sysfs attributes, reset/resume behavior, and orchestration of optional LCD/backlight/framebuffer/LED/CIR/debugfs submodules.

## Important APIs, types, and functions
`picolcd_driver` registers callbacks for probe, remove, raw_event, suspend, resume, and reset_resume. `picolcd_report` finds input/output reports by ID. `picolcd_send_and_wait` serializes a single output report, stores a `picolcd_pending`, submits SET_REPORT, and waits up to two seconds for raw input completion. `picolcd_reset` sends `REPORT_RESET`, checks version, then restores LCD/backlight/framebuffer/LED state. `picolcd_raw_event` dispatches key state, IR data, and pending responses. `picolcd_probe_lcd` and `picolcd_probe_bootloader` select normal-mode or bootloader initialization.

## Control flow
Probe allocates `picolcd_data`, initializes lock/mutex/default mode delay, marks bootloader mode from product ID, parses descriptors, starts and opens HID, creates `operation_mode_delay` and `operation_mode` sysfs attributes, then initializes either normal LCD subsystems or bootloader debugfs flash access. Normal mode setup is ordered as keypad, CIR, LCD, backlight, framebuffer, LEDs, and debugfs; failures unwind in reverse feature order.

Raw events are consumed by this driver. `REPORT_KEY_STATE` updates the keypad input device, tracking up to two currently pressed keys and emitting scan/key press/release events. `REPORT_IR_DATA` is forwarded to CIR. Other reports complete the currently pending synchronous command by copying payload bytes after the report ID into `pending->raw_data`, setting `raw_size` and `in_report`, and completing the wait. Debug raw-event logging is called after dispatch.

Remove sets `PICOLCD_FAILED`, removes debugfs and sysfs, closes/stops HID, completes any pending wait that would otherwise hang, tears down optional subdevices, destroys the mutex, and frees `picolcd_data`.

## State and persistence behavior
`picolcd_data` stores firmware version, mode delay, pressed keys, keymap, optional subdevice pointers, `pending`, and status bits. `operation_mode_delay` is mutable through sysfs and used when switching between LCD and bootloader mode. No settings are persisted across unplug. The pending command slot is protected by `data->mutex` and `data->lock`; `PICOLCD_FAILED` prevents new report submissions and shortcuts teardown.

## Dependencies and integration points
The file integrates with HID core, input, fbdev/vmalloc headers, completion, sysfs, and every PicoLCD companion module through `hid-picolcd.h`. It binds Microchip PicoLCD normal and bootloader product IDs.

## Risks and test signals
Key risks are pending-command races, missed completions, mode switching while userspace holds debugfs files, and teardown ordering with framebuffer deferred work. Test signals include keypad press/release including unknown keys, IR dispatch, version query, operation-mode sysfs reads/writes, reset/resume preserving display/backlight/LED state, bootloader probe, and disconnect while `picolcd_send_and_wait` is waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_core.c -->
