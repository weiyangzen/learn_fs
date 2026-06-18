<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd.h

## Purpose
This header is the shared contract for the PicoLCD graphic HID driver split across core, framebuffer, LCD, backlight, LED, CIR, and debugfs modules. It defines report IDs, shared per-device state, pending synchronous request state, framebuffer private data, feature flags, and optional subsystem entry points.

## Important APIs, types, and functions
Report constants cover normal LCD mode and bootloader mode: key state, IR data, EEPROM data/read/write, flash memory read/write/erase, brightness, contrast, reset, LCD command/data, version, device ID, splash, hook version, and mode-exit reports. `struct picolcd_pending` stores one in-flight output report and its eventual input response with a completion and raw data buffer. `struct picolcd_data` is the central device object containing `hdev`, version, mode delay, key state, optional rc/framebuffer/lcd/backlight/LED/debugfs members, `lock`, `mutex`, `pending`, and status flags (`PICOLCD_BOOTLOADER`, `PICOLCD_FAILED`, `PICOLCD_CIR_SHUN`).

`struct picolcd_fb_data` holds framebuffer-side state: lock, back-pointer to `picolcd_data`, update rate, bits-per-pixel, force/ready flags, translated `vbitmap`, and framebuffer `bitmap`. The header declares `picolcd_report`, `picolcd_reset`, and `picolcd_send_and_wait`; it also provides optional stubs when feature Kconfig symbols are disabled.

## Control flow
The header enables core code to call subsystem setup/teardown functions without conditional call sites. For enabled features, real functions are linked; otherwise inline stubs return success or no-op. It also wraps `hid_hw_request` under `CONFIG_DEBUG_FS` so outgoing reports are decoded by `picolcd_debug_out_report` before the actual HID request.

## State and persistence behavior
The state is per attached PicoLCD device and is not persisted across disconnect. `pending` is the single synchronous command slot, protected by the device spinlock and serialized by `mutex` in core. Status bits coordinate mode, failed teardown, and CIR open/close behavior across modules.

## Dependencies and integration points
This header bridges HID core with input, rc-core, fbdev, lcd, backlight, LED class, debugfs, completion, and module/Kconfig conditionals. It is the integration point that keeps the split PicoLCD files source-compatible under multiple feature configurations.

## Risks and test signals
The major risk is cross-module lifetime: optional pointers can be NULL depending on Kconfig and probe stage, so callers must honor the stubs and null checks. The debugfs `hid_hw_request` macro changes call behavior in all including files when debugfs is enabled, so recursion avoidance and side-effect ordering matter. Test signals include builds with each PicoLCD feature enabled/disabled, sparse/compile checks for the macro path, and runtime reset/remove while a `picolcd_pending` wait is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd.h -->
