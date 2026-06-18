# subset-b-003805 HID source research

Grouped research for HID driver files under `sources/distributed-fs/ceph-client/drivers/hid`. Each file section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nvidia-shield.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-nvidia-shield.c

## Purpose
This file implements the NVIDIA SHIELD HID driver, currently centered on the Thunderstrike controller over USB or Bluetooth. It replaces generic HID behavior where needed with explicit Android-style key mapping, a haptics input device, an LED class device, a power_supply battery device, and sysfs attributes for firmware, hardware revision, and serial number. The device-specific protocol is a 33-byte "HOSTCMD" request/response report pair: output report 0x4 carries commands and input report 0x3 returns command payloads.

## Important APIs, types, and functions
The public integration point is `shield_driver`, whose callbacks are `shield_probe`, `shield_remove`, `shield_raw_event`, and `android_input_mapping`. `struct shield_device` is the common base containing `hdev`, battery descriptor, initialization flags, codename, firmware version, and board info. `struct thunderstrike` embeds that base and adds an allocated ID, haptics input device, LED classdev, request DMA buffer, update flags, haptics state, power-supply cached stats, timer, and work item.

The packed report structures (`thunderstrike_hostcmd_req_report`, `thunderstrike_hostcmd_resp_report`, and payload structs) define the on-wire ABI. `static_assert` checks keep the C layout aligned with the fixed report size. `thunderstrike_hostcmd_req_work_handler` serializes queued requests using `update_flags`; `thunderstrike_parse_report` demultiplexes HOSTCMD responses by `cmd_id`. Power state is exposed through `thunderstrike_battery_get_property`; LEDs use `thunderstrike_led_get_brightness` and `thunderstrike_led_set_brightness`; haptics use `thunderstrike_play_effect`.

## Control flow
Probe calls `hid_parse`, constructs a Thunderstrike device from the product ID, starts HID input connection, opens the device, then calls `thunderstrike_device_init_info`. Creation allocates the request buffer, initializes locks/work, assigns an ID from `thunderstrike_ida`, creates optional force feedback, registers the battery and LED devices, and sets up the five-minute battery timer. Initial info requests are not sent inline; they set update bits and schedule `hostcmd_req_work`.

The work handler processes firmware, LED, battery/charger, board-info, and haptics update bits in a fixed order. Each command fills the shared request buffer and submits it via `hid_hw_raw_request`. Raw input report 0x3 reaches `shield_raw_event`, then `thunderstrike_parse_report`; firmware and board info set initialization flags, LED responses update cached brightness, battery and charger responses convert device units into Linux `power_supply` values, and USB-init/charger responses can trigger deferred initialization requests.

Remove closes HID, unregisters subdevices, deletes the power-supply timer, cancels pending work, frees the ID, and stops HID. One noteworthy ordering detail is that `thunderstrike_destroy` unregisters LED/power/input and frees the ID before `timer_delete_sync` and `cancel_work_sync`; future edits should keep use-after-free risk in mind if any work/timer callback is extended to touch unregistered subdevices.

## State and persistence behavior
State is runtime-only. Initialization flags in `shield_device.initialized_flags` gate sysfs output, returning `NOT INITIALIZED` until reports arrive. Haptics and LED requests are coalesced through `update_flags`; haptics values are protected by `haptics_update_lock`, and battery/charger cached values by `psy_stats_lock`. Battery properties are cached until the periodic timer refreshes every five minutes. The IDA-assigned Thunderstrike ID affects LED and power-supply names but is released on remove.

## Dependencies and integration points
The file depends on HID core, input, force-feedback memless support when `CONFIG_NVIDIA_SHIELD_FF` is enabled, LED class, power_supply, timers, workqueues, IDA allocation, and `hid-ids.h`. It exposes normal input key mappings for Android consumer usages, a separate haptics input device, a `thunderstrike%d:blue:led` LED, `thunderstrike_%d` battery, and three device sysfs attributes via `dev_groups`.

## Risks and test signals
Key risks are report-size mismatch, packed ABI drift, concurrency around the shared output buffer, and lifecycle ordering between timers/work and unregister/free. The parser has explicit size checks for HOSTCMD responses and warns on unknown command IDs. Useful tests include connecting both USB and Bluetooth Thunderstrike devices, reading sysfs before and after initialization, toggling LED brightness, force-feedback rumble, power_supply capacity/status refresh across charger states, suspend/resume LED retention, and disconnect during pending timer/work activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nvidia-shield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c

## Purpose
This is a small HID descriptor-fix driver for Ortek-family keyboards/trackpads and a Skycable wireless presenter. The supported devices have incorrect logical maximum values in their report descriptors, causing consumer/page usages to be truncated or misinterpreted by generic HID parsing.

## Important APIs, types, and functions
The primary callback is `ortek_report_fixup`, installed in `ortek_driver.report_fixup`. It receives the mutable descriptor buffer and descriptor size before HID parsing. The device table binds Ortek PKB-1700, WKB-2000, iHome IMAC-A210S, and Skycable wireless presenter IDs from `hid-ids.h`.

## Control flow
There is no custom probe/remove path. HID core matches one of the IDs, calls `ortek_report_fixup` during parse, and then generic HID handling continues. The fixup checks exact descriptor offsets: for Ortek descriptors it changes byte 55 after a `0x25` logical maximum item from `0x01` to `0x92`; for Skycable it changes byte 53 from `0x01` to `0x65`. If the size/byte pattern does not match, the descriptor is returned unchanged.

## State and persistence behavior
The driver has no persistent state and allocates no per-device data. Its only mutation is in-place descriptor repair during enumeration.

## Dependencies and integration points
It depends only on HID core, module infrastructure, device headers, and `hid-ids.h`. After descriptor repair, all runtime input event generation is delegated to generic HID input handling.

## Risks and test signals
The risk is offset-specific descriptor patching: a firmware variant with a similar product ID but different descriptor layout may not be repaired or could be repaired incorrectly if the byte guard is too weak. The guards check descriptor length and local byte patterns. Test signals are descriptor dumps before/after fixup, successful parsing of high consumer usages, and no regression for the four listed device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ortek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c

## Purpose
This driver provides a minimal input mapping quirk for PenMount 6000 HID touchscreens. It remaps the first button usage to `BTN_TOUCH` and rejects additional button usages, making the touch contact semantics line up with Linux touchscreen input expectations.

## Important APIs, types, and functions
`penmount_input_mapping` is the only behavioral callback. It is registered in `penmount_driver.input_mapping`. The device table binds `USB_VENDOR_ID_PENMOUNT` and `USB_DEVICE_ID_PENMOUNT_6000`.

## Control flow
Generic HID parsing and hardware start are used. During input mapping, usages on `HID_UP_BUTTON` are inspected. Usage button 1 maps to `EV_KEY/BTN_TOUCH` via `hid_map_usage`; all other button usages return `-1`, telling HID input mapping to ignore them. Non-button usages return 0 so generic mapping can process coordinates and other fields.

## State and persistence behavior
No private state is allocated. The only lasting effect is the input device capability mapping created during probe.

## Dependencies and integration points
The file integrates with HID input mapping and Linux input event codes. Coordinate processing remains generic; this file only corrects touch button semantics.

## Risks and test signals
Risks are limited to button usage interpretation. Devices that use multiple meaningful buttons would lose them, but this is deliberate for the matched touchscreen. Tests should verify `BTN_TOUCH` press/release appears with coordinate reports and that extra button usages are not exposed as spurious keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-penmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c

## Purpose
This driver supports the Petalynx Maxter Remote by fixing a too-low consumer usage maximum, mapping vendor-specific remote buttons to Linux key codes, and forcing `HID_QUIRK_NOGET` during probe. It is a device quirk driver layered on normal HID input handling.

## Important APIs, types, and functions
`pl_report_fixup` patches descriptor maximum values when a precise descriptor pattern is present. `pl_input_mapping` maps Logitech/vendor-page usages 0x05a-0x05e to text/color keys and consumer usages 0x0f6/0x0fa to next/back. `pl_probe` sets `HID_QUIRK_NOGET`, calls `hid_parse`, then starts hardware with `HID_CONNECT_DEFAULT`.

## Control flow
On match, custom probe sets the no-get quirk before parse/start. Descriptor fixup runs during parse and changes both the usage maximum and logical maximum from `0xf9`/`0xf5` style limits to `0xfa` where the exact report bytes match. Input mapping handles selected vendor and consumer usages with `hid_map_usage_clear`, returning 1 for mapped usages and 0 for generic fallback.

## State and persistence behavior
There is no per-device allocation. The persistent runtime effects are the HID quirk bit, patched descriptor bytes, and the input mapping table installed in the input device.

## Dependencies and integration points
The file depends on HID core, Linux key codes, and `hid-ids.h`. Its output is a normal HID input device with corrected key capabilities.

## Risks and test signals
Risks include overly specific descriptor offsets and the broad `NOGET` quirk potentially hiding feature reports if future devices reuse the ID with different behavior. Tests should cover all remapped keys, descriptor parsing with the original Maxter descriptor, and probe/start behavior when GET_REPORT would otherwise fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-petalynx.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c

## Purpose
This module exposes PicoLCD backlight brightness through the Linux backlight class and translates brightness/power changes into `REPORT_BRIGHTNESS` HID output reports.

## Important APIs, types, and functions
`picolcd_blops` provides `.update_status = picolcd_set_brightness` and `.get_brightness = picolcd_get_brightness`. `picolcd_init_backlight` validates the brightness report shape, registers a `BACKLIGHT_RAW` device, sets default brightness 0xff, and sends it to hardware. `picolcd_exit_backlight`, `picolcd_resume_backlight`, and `picolcd_suspend_backlight` handle teardown and power management restore.

## Control flow
Probe passes the brightness output report from core into `picolcd_init_backlight`. Runtime updates come from the backlight class into `picolcd_set_brightness`, which caches `lcd_brightness` and `lcd_power`, sets the single report field to either the brightness value or zero when powered off, and submits a SET_REPORT under `data->lock` if the device has not failed.

## State and persistence behavior
Backlight state is held in `picolcd_data.lcd_brightness`, `lcd_power`, and `backlight`. It is restored on resume/reset by replaying the cached brightness. No state is persisted beyond the attached device lifetime.

## Dependencies and integration points
The module depends on HID output reports, the backlight subsystem, and the shared PicoLCD lock/status fields. Framebuffer code may attach the backlight to `fb_info` when `CONFIG_FB_BACKLIGHT` is enabled.

## Risks and test signals
Risks include invalid report descriptors, null `data->backlight` during cleanup, and races with device removal. Tests should vary brightness and blanking, suspend/resume, reset-resume, removal after registration, and Kconfig combinations with framebuffer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c

## Purpose
This module turns PicoLCD IR receiver HID packets into rc-core raw IR events. It registers an `rc_dev` for raw IR decoding and interprets HID interval data as pulse/space durations in microseconds.

## Important APIs, types, and functions
`picolcd_raw_cir` is called from core raw-event handling for `REPORT_IR_DATA`. `picolcd_init_cir` allocates/registers an `RC_DRIVER_IR_RAW` device with `RC_PROTO_BIT_ALL_IR_DECODER`, `RC_MAP_RC6_MCE`, 100 ms timeout, and 1 us resolution. `picolcd_cir_open` clears `PICOLCD_CIR_SHUN`; `picolcd_cir_close` sets it; `picolcd_exit_cir` unregisters and frees the rc device.

## Control flow
Raw IR data begins with a length byte. The handler ignores input when `rc_dev` is absent or CIR is shunned, then parses 16-bit big-endian interval words. The high bit means pulse and stores a negated-duration encoding; pulse duration is converted with `65536 - w`, while spaces use the raw value. A first interval greater than 15000 us is reduced by 15000 as a device-specific quirk before events are stored and flushed with `ir_raw_event_handle`.

## State and persistence behavior
The module stores only `data->rc_dev` and the `PICOLCD_CIR_SHUN` bit. Open/close controls whether incoming IR data is consumed. No learned remotes or decoded keys are persisted here; rc-core/user space owns protocol decoding configuration.

## Dependencies and integration points
It integrates HID raw reports with media `rc-core`, input identity fields from the HID device, and the shared PicoLCD lock/status. Core dispatches only the report payload, skipping the report ID byte.

## Risks and test signals
Risks are malformed length bytes, interval interpretation quirks, and remove races while raw reports arrive. Tests should open/close the rc device, verify raw event timing with known remotes, check the >15000 us first-interval adjustment, and disconnect during active IR input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_cir.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c

## Purpose
This module provides PicoLCD debugfs controls and HID report tracing. It exposes `reset`, `eeprom`, and `flash` debugfs files when corresponding reports exist, implements EEPROM/flash read/write protocols using synchronous HID commands, and decodes outgoing/incoming reports into the HID debug stream.

## Important APIs, types, and functions
Debugfs file operations include `picolcd_debug_reset_fops`, `picolcd_debug_eeprom_fops`, and `picolcd_debug_flash_fops`. EEPROM handlers use `REPORT_EE_READ`, `REPORT_EE_WRITE`, and expect `REPORT_EE_DATA`. Flash helpers `_picolcd_flash_read`, `_picolcd_flash_erase64`, and `_picolcd_flash_write` support both LCD mode (`REPORT_READ_MEMORY`, `REPORT_ERASE_MEMORY`, `REPORT_WRITE_MEMORY`) and bootloader mode (`REPORT_BL_*`). `picolcd_debug_out_report` and `picolcd_debug_raw_event` decode many report IDs for `hid_debug_event`. `picolcd_init_devfs` creates debugfs files and determines flash address width; `picolcd_exit_devfs` removes them and destroys `mutex_flash`.

## Control flow
Reset debugfs writes accept `all` or `fb`, calling `picolcd_reset` and/or `picolcd_fb_reset`. EEPROM reads/writes operate in chunks of up to 20 bytes, send address/length/data payloads, and verify the echoed response before copying to/from userspace. Flash reads loop in up to 32-byte chunks within the 0x0000-0x5fff range. Flash writes require 64-byte alignment and size multiples, lock `mutex_flash`, erase each 64-byte block, write it in chunks, and stop on the first error.

Report debug functions are invoked by the header macro wrapping `hid_hw_request` and by core raw-event dispatch. They allocate temporary buffers, dump raw bytes as hex, decode known report fields, emit messages to `hdev->debug_list`, and wake `debug_wait`.

## State and persistence behavior
Debugfs state lives in `picolcd_data.debug_reset`, `debug_eeprom`, `debug_flash`, `mutex_flash`, and `addr_sz`. Flash/EEPROM writes affect persistent device memory, unlike most other PicoLCD state. Partial flash write failures are explicitly documented as leaving the target block undefined.

## Dependencies and integration points
The module depends on debugfs, seq_file, HID debug infrastructure, userspace copy helpers, hex formatting, and the core synchronous `picolcd_send_and_wait` path. It integrates with normal and bootloader report IDs.

## Risks and test signals
This is the highest-risk PicoLCD surface because it writes device EEPROM/flash from debugfs. Risks include partial writes after erase, address-size misdetection, userspace copy failures mid-operation, unchecked raw report sizes in debug decode paths, and concurrent access outside flash writes. Tests should cover read boundaries, zero-length handling, unaligned flash write rejection, 64-byte write/erase verification, bootloader reports, debug tracing enabled/disabled, and disconnect during synchronous debugfs I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c

## Purpose
This module exposes the PicoLCD 256x64 monochrome display as a Linux fbdev framebuffer. It translates packed or 8-bit grayscale framebuffer memory into the display controller's tile format and sends only changed tiles through LCD command/data HID reports.

## Important APIs, types, and functions
Constants define a 256x64 display and 2048-byte 1bpp device bitmap. `picolcd_fb_send_tile` emits one tile using `REPORT_LCD_CMD_DATA` and `REPORT_LCD_DATA`. `picolcd_fb_update_tile` translates framebuffer pixels into the PicoLCD vertical-byte tile layout and detects changes. `picolcd_fb_update` scans all 4 chips x 8 tiles and throttles against `HID_OUTPUT_FIFO_SIZE` with `hid_hw_wait`. Fbdev operations are in `picolcdfb_ops`; deferred I/O is provided by `picolcd_fb_deferred_io`. `picolcd_init_framebuffer` allocates/registers fb_info and sysfs `fb_update_rate`; `picolcd_exit_framebuffer` disconnects and unregisters it.

## Control flow
Initialization allocates one fb_info block containing deferred I/O metadata, pseudo palette, `picolcd_fb_data`, and vbitmap storage, then vmallocs the user framebuffer. It resets the LCD controller, creates update-rate sysfs, initializes deferred I/O, and registers the framebuffer. Damage callbacks schedule immediate deferred work. The update path locks the framebuffer, resets the display if not ready, translates changed tiles, sends changed or forced tiles, waits when the HID output FIFO may fill, and clears the force flag on success.

`picolcd_fb_reset` sends LCD mapping commands to all four chips, optionally clears cached/device framebuffer memory, marks `force`, and schedules the first output once ready. `picolcd_set_par` supports switching between 1bpp and 8bpp by translating existing content.

## State and persistence behavior
Framebuffer state is runtime memory only: `bitmap` is the userspace-visible buffer, `vbitmap` is the last sent device-format image, `force` triggers full refresh, `ready` tracks initial reset, and `update_rate` controls deferred I/O delay. Display contents can be restored after reset/resume from `bitmap`.

## Dependencies and integration points
The module integrates with fbdev, deferred I/O, optional backlight/LCD devices, HID output reports, and the shared PicoLCD `data->lock` and failed status. It is called from core probe, reset, raw power-management restore, and remove.

## Risks and test signals
Risks include deferred work racing with disconnect, tile translation errors across 1bpp/8bpp modes, HID FIFO flooding, and invalid report descriptors. The code mitigates teardown by nulling `fbdata->picolcd` under lock and flushing deferred work before unregister. Tests should draw patterns covering every chip/tile, switch bpp, tune `fb_update_rate`, reset/resume with retained contents, and disconnect during active framebuffer writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c

## Purpose
This module exposes PicoLCD contrast through the Linux LCD class and translates contrast changes into the one-byte `REPORT_CONTRAST` HID output report.

## Important APIs, types, and functions
`picolcd_lcdops` implements `.get_contrast` and `.set_contrast`. `picolcd_init_lcd` validates the contrast output report, registers an `lcd_device`, sets max contrast 0xff, caches default contrast 0xe5, and sends it to hardware. `picolcd_exit_lcd` unregisters the LCD class device. `picolcd_resume_lcd` replays cached contrast after reset/resume.

## Control flow
Core probe passes the contrast report into `picolcd_init_lcd`. Runtime LCD class updates call `picolcd_set_contrast`, which masks the requested value to 8 bits, writes the report field under `data->lock`, and submits SET_REPORT if the device is not marked failed.

## State and persistence behavior
Only the cached `data->lcd_contrast` and `data->lcd` pointer are maintained. Contrast is restored from memory after reset/resume, but not persisted across unplug.

## Dependencies and integration points
It depends on HID reports and the LCD subsystem. Framebuffer code may attach this LCD device to fb_info for fb blanking/notification integration.

## Risks and test signals
Risks are report shape mismatch, null teardown, and removal races during class callbacks. Tests should validate contrast sysfs/class controls, default contrast setup, resume/reset restore, and builds with/without framebuffer and backlight modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c

## Purpose
This module exposes PicoLCD's eight general-purpose output bits as LED class devices named `GPO0` through `GPO7`, and writes their combined bitmask through `REPORT_LED_STATE`.

## Important APIs, types, and functions
`picolcd_leds_set` sends the cached bitmask to hardware. `picolcd_led_set_brightness` and `picolcd_led_get_brightness` implement per-LED class operations by locating the LED pointer in `data->led[]`. `picolcd_init_leds` validates the LED report and registers eight allocated `led_classdev` instances. `picolcd_exit_leds` unregisters and frees them.

## Control flow
On initialization, each LED classdev is allocated with space for its name, registered, and stored in `data->led[i]`. Setting brightness toggles the corresponding bit in `data->led_state`; if the bit changes, the aggregate state is sent under `data->lock`. `picolcd_leds_set` is also called after reset to restore the cached output state.

## State and persistence behavior
The LED state is an 8-bit runtime cache in `data->led_state` plus the registered LED pointers. It is restored after reset/resume but is not stored persistently.

## Dependencies and integration points
The module depends on HID output reports, LED class, and the shared PicoLCD lock/status. LED class callbacks derive `hdev` from the parent device to recover `picolcd_data`.

## Risks and test signals
Risks include partially registered LEDs on allocation failure, pointer arithmetic in brightness callbacks, and updates during removal. Tests should toggle each GPO independently, verify aggregate report bytes, test registration failure unwind, reset restore, and remove while LEDs are visible in sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c

## Purpose
This driver supports PantherLord/GreenAsia-compatible gamepads and adapters, mainly adding optional force-feedback rumble support and multi-input handling for dual adapters. It leaves ordinary input parsing to HID core after custom probe setup.

## Important APIs, types, and functions
When `CONFIG_PANTHERLORD_FF` is enabled, `struct plff_device` stores the output report, maximum rumble value, and pointers to strong/weak output fields. `hid_plff_play` scales Linux `FF_RUMBLE` magnitudes into device report values and submits the output report. `plff_init` inspects HID output reports and input devices to attach memless force feedback. `pl_probe` handles quirks, parsing, hardware start, and force-feedback init.

## Control flow
Probe sets `HID_QUIRK_MULTI_INPUT` for dual adapter IDs using `driver_data`, parses the descriptor, starts hardware with force-feedback auto-connect disabled, then calls `plff_init`. The FF initializer walks each HID input and corresponding output report. It supports two report layouts: one field with at least four values, or four separate fields with specific LED usage patterns. It stores pointers to the strong/weak value locations, initializes them to zero, sends an initial report, and registers memless rumble with the input device.

## State and persistence behavior
Per-input force-feedback state is allocated as `plff_device` and owned by the input FF memless data path. The output report fields hold current rumble values. No state is persisted across unplug.

## Dependencies and integration points
The file depends on HID core, input force feedback, optional `CONFIG_PANTHERLORD_FF`, and IDs for Gameron, GreenAsia, and Jess/Saitek devices. It integrates with Linux input `FF_RUMBLE` and HID output reports.

## Risks and test signals
Risks include output report layout assumptions, mismatching report count to input devices, and value scaling differences between 0x7f and 0xff devices. Tests should cover single-field and four-field devices, dual adapter multi-input enumeration, rumble magnitude scaling, missing output reports, and builds with FF disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c

## Purpose
This driver normalizes Plantronics USB HID headset controls. It maps vendor-specific and telephony/consumer volume/mute usages to Linux input keys, forces HID input/hiddev exposure, and filters duplicate key presses that some devices emit within a few milliseconds.

## Important APIs, types, and functions
`struct plt_drv_data` stores decoded device type, last key timestamp, double-key timeout, and last key code. `plantronics_device_type` decodes either product ID for multi-HID interfaces or primary vendor collection usage. `plantronics_input_mapping` decides whether usages should be ignored, defaulted, or mapped to `KEY_VOLUMEUP`, `KEY_VOLUMEDOWN`, or `KEY_MICMUTE`. `plantronics_event` filters repeated key-down events. `plantronics_probe` allocates state, parses, determines type, initializes duplicate filtering, and starts HID.

## Control flow
Probe parses first because collection data is needed to classify device type. For BT300-style multi-HID interfaces, the product ID remains the type; otherwise collection usages on Plantronics HID 1.0/2.0 vendor pages select the type. Input mapping allows generic consumer controls and telephony mute where appropriate, handles DA60 special mute mapping, maps vendor controls for non-basic-telephony devices, and ignores unrelated usages. The usage table limits `.event` callbacks to relevant volume/mute usages, where duplicate presses of the same key within `PLT_DOUBLE_KEY_TIMEOUT` are consumed.

## State and persistence behavior
State is per device and allocated with devm. Duplicate filtering uses `jiffies`, stores only the last key and timestamp, and is disabled if HZ granularity cannot represent the 5 ms timeout. No persistent state exists.

## Dependencies and integration points
The file integrates HID input mapping, HID usage filtering, Linux input key codes, hiddev forced connection, and Plantronics vendor usage pages. It exposes normal input events to userspace and keeps hiddev available for legacy/control applications.

## Risks and test signals
Risks include device classification errors, suppressing legitimate fast repeated presses, and mapping changes for basic telephony compliant devices. Tests should cover DA60, BT300 range, HID 1.0/2.0 vendor pages, standard consumer controls, mic mute, duplicate filtering at HZ-dependent boundaries, and hiddev/input node creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c

## Purpose
This is the main Sony PlayStation HID driver for DualShock 4 and DualSense controllers over USB and Bluetooth, including the DualShock 4 USB dongle. It creates its own input devices for gamepad, sensors, touchpad, and DualSense headset jack; registers battery and LED devices; handles force feedback; validates Bluetooth CRCs; reads calibration/firmware/pairing feature reports; and sends output reports for rumble, lightbars, player LEDs, audio routing, microphone mute, and Bluetooth poll interval.

## Important APIs, types, and functions
`struct ps_device` is the base object for all supported controllers, holding the HID device, spinlock, player ID, battery state, MAC address, versions, and virtual parse/remove callbacks. `struct dualsense` and `struct dualshock4` embed the base and add device-specific input devices, calibration data, timestamp state, output update flags, LED state, rumble state, work items, and report buffers.

Important common helpers include `ps_devices_list_add/remove` for duplicate MAC detection, `ps_device_set_player_id/release`, `ps_gamepad_create`, `ps_sensors_create`, `ps_touchpad_create`, `ps_headset_jack_create`, `ps_get_report`, `ps_check_crc32`, `ps_device_register_battery`, `ps_led_register`, and `ps_lightbar_register`. Device-specific creation paths are `dualsense_create` and `dualshock4_create`; parsing paths are `dualsense_parse_report`, `dualshock4_parse_report`, and `dualshock4_dongle_parse_report`; output workers are `dualsense_output_worker` and `dualshock4_output_worker`.

## Control flow
Module init registers `ps_driver`. Probe parses HID, starts only `HID_CONNECT_HIDRAW`, opens the device, and dispatches by `driver_data` to DualShock 4 or DualSense creation. Creation patches the HID version with `HID_PLAYSTATION_VERSION_PATCH`, initializes locks/work and output buffers, gets MAC address, reads firmware and calibration feature reports, rejects duplicate MACs, creates input devices, registers battery and LEDs, assigns player ID, and schedules initial LED/output state. Remove removes the device from the global list, releases player ID, disables/cancels output work, closes HID, and stops hardware.

Raw input reports enter `ps_raw_event` and then the device-specific parser. DualSense supports USB report 0x01 and Bluetooth report 0x31 with CRC validation; it reports gamepad axes/buttons, toggles hardware microphone mute on button edge, routes USB headset audio based on jack status, calibrates motion sensors, emits monotonic sensor timestamps, reports two touch contacts, and updates cached battery status. DualShock 4 supports USB report 0x01, full Bluetooth report 0x11 with CRC, and minimal Bluetooth report 0x01 for third-party pads; it reports gamepad data, sensors, multiple touch reports, touchpad button, and battery state. The USB dongle wrapper waits for connection, calibrates asynchronously, and suppresses reports until connected/calibrated.

Output state is coalesced through spinlock-protected flags and a workqueue. DualSense output reports differ for USB and Bluetooth; Bluetooth reports include sequence/tag fields and CRC. DualShock 4 Bluetooth output reports set HID/CRC control flags and may include poll interval. Force feedback callbacks scale `FF_RUMBLE` to bytes and schedule work. LED class callbacks update cached colors/player states and schedule output.

## State and persistence behavior
All state is per attachment and runtime-only. The global device list prevents duplicate USB+Bluetooth connections for the same MAC. Player IDs come from a module-global IDA and are released on remove; `ida_destroy` runs at module exit. Battery state is cached under `ps_device.lock` and exposed via power_supply. Sensor timestamps are expanded from device counters with wrap handling. Output flags are cleared after each worker builds a report, so rapid updates coalesce.

## Dependencies and integration points
The driver depends on HID core, hidraw, Linux input/multitouch, memless force feedback when enabled, power_supply, LED and multicolor LED class, CRC32, IDA/list/mutex/spinlock/workqueue primitives, and unaligned endian helpers. It exposes sysfs `firmware_version` and `hardware_version` through driver device groups, plus input nodes, power supplies, and LED class devices.

## Risks and test signals
Major risks are report ABI drift across controller firmware, Bluetooth CRC handling, calibration denominator zero or invalid feature reports, duplicate-device lifecycle, output worker races on disconnect, and third-party controller deviations. The code includes report-size/ID checks, CRC checks, calibration fallback for invalid denominators, and dongle state gating. Tests should cover USB/BT DualShock 4, USB/BT DualSense, DualSense Edge/product 2 behavior, DS4 dongle hotplug, hidraw coexistence during feature reports, rumble/LED/mic/headset output, battery state transitions, touchpad MT events, sensor calibration and timestamp wrap, duplicate MAC rejection, and removal during queued output work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c

## Purpose
This driver fixes Primax keyboards that send modifier keys in-band in the key array instead of in the modifier byte. It rewrites raw keyboard input reports so generic HID keyboard handling sees standard modifier bits.

## Important APIs, types, and functions
`px_raw_event` is the only behavioral callback and is registered as `.raw_event` in `px_driver`. The device table binds `USB_VENDOR_ID_PRIMAX` and `USB_DEVICE_ID_PRIMAX_KEYBOARD`.

## Control flow
For report ID 0, the handler scans report bytes from the end down to index 2. Values 0xe0 through 0xe7 are USB HID modifier key usages. Each such value sets the corresponding bit in `data[0]` and clears the in-band key slot to zero. The adjusted report is immediately fed back into HID parsing through `hid_report_raw_event`, and the callback returns 1 to consume the original report. Unknown report IDs are logged and passed upstream.

## State and persistence behavior
No per-device state exists. The mutation is per input report and only affects the current event buffer.

## Dependencies and integration points
The file integrates with HID raw-event handling and generic HID keyboard parsing. It depends on the report being unnumbered/report ID 0 keyboard input with standard modifier usages.

## Risks and test signals
Risks are report layout assumptions and recursion or double-processing if the consumed return value changes. Tests should send reports with left/right modifiers in key slots, mixed normal keys, no modifiers, and unknown reports; expected output is one standard keyboard event stream with modifier bits set and no phantom key usages 0xe0-0xe7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-primax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c

## Purpose
This driver supports the Creative Prodikeys PC-MIDI keyboard. It combines HID keyboard handling, extra multimedia/function keys, a vendor output report for mode/LED state, and an ALSA raw MIDI input device that converts the musical keyboard reports into MIDI note events. It also exposes sysfs controls for MIDI channel, octave shift, and sustain duration.

## Important APIs, types, and functions
`struct pcmidi_snd` is the per-interface state object: HID device, USB interface number, output report 6, extra-key input device pointer, MIDI mode/sustain/channel/octave state, sustain timers, function state, last-key cache, rawmidi lock/substream/trigger state, and ALSA card/rawmidi pointers. `struct pcmidi_sustain` stores delayed note-off events.

Sysfs handlers are `show/store_channel`, `show/store_sustain`, and `show/store_octave`. MIDI/event handling is split across `pcmidi_handle_report1`, `pcmidi_handle_report3`, `pcmidi_handle_report4`, `pcmidi_handle_report`, `pcmidi_send_note`, and `pcmidi_sustained_note_release`. ALSA setup/teardown is in `pcmidi_snd_initialise` and `pcmidi_snd_terminate`. HID callbacks are `pk_report_fixup`, `pk_input_mapping`, `pk_raw_event`, `pk_probe`, and `pk_remove`.

## Control flow
Probe requires USB, determines the interface number, allocates state, parses HID, restores `HID_QUIRK_NOGET` when requested, starts HID, and initializes ALSA only for interface 1. Report fixup corrects report 4 count in a known 178-byte descriptor. Input mapping for Microsoft vendor page on interface 1 records the input device and adds extra key capabilities.

Raw reports on interface 1 are intercepted for report IDs 1, 3, and 4. Report 1 handles qwerty MIDI-mode special keys such as octave down and sustain toggle. Report 3 converts note pairs into MIDI note-on/note-off bytes using middle C, current channel, and octave; sustain mode delays note-off by arming one of 32 timers. Report 4 handles extra office/media keys, Fn lock, MIDI launcher/mode toggle, octave up in MIDI mode, and emits key press/release events through the captured input device. Output report 6 is used to set device mode/state bytes such as 0xc1, 0xc5, and 0xc6.

ALSA initialization creates an `snd_card`, low-level device, one-input rawmidi device, sysfs attributes, spinlock, sustain timers, output-report operational state, and then registers the card. The rawmidi trigger path gates whether `pcmidi_send_note` delivers bytes to the current input substream.

## State and persistence behavior
MIDI channel, octave, sustain duration, MIDI mode, Fn state, last pressed extra keys, and in-flight sustain timers are runtime state only. Sysfs writes update in-memory controls. Sustain timers persist delayed note-off events until they fire or `stop_sustain_timers` deletes them during teardown. ALSA card lifetime can extend until userspace closes it because removal uses `snd_card_disconnect` and `snd_card_free_when_closed`.

## Dependencies and integration points
The driver depends on HID core, USB interface metadata, Linux input, timers, spinlocks, ALSA core/rawmidi, module parameters (`index`, `id`, `enable`), sysfs, and `hid-ids.h`. It integrates one physical HID device with both input and sound subsystems.

## Risks and test signals
Risks include interface-number assumptions, rawmidi lock/substream races, timer-delayed note-off after removal, failure unwind across ALSA/sysfs/timers, and note arithmetic outside valid MIDI ranges when octave shifts combine with device note values. Tests should verify descriptor fixup, interface 1-only ALSA creation, channel/octave/sustain sysfs validation, note-on/off conversion, sustain timer release and teardown, extra key press/release state, MIDI mode toggles, rawmidi open/trigger gating, and removal while ALSA clients are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-prodikeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c

## Purpose
This driver supports the PhoenixRC 8-axis flight controller by replacing the broken device report descriptor with a fixed joystick descriptor and rewriting alternating raw reports so the shared last byte becomes stable slider and dial axes.

## Important APIs, types, and functions
`struct pxrc_priv` stores cached slider, cached dial, and an `alternate` toggle. `pxrc_rdesc_fixed` is the replacement HID descriptor declaring a joystick with X, Slider, Y, Z, Rx, Ry, Rz, and Dial axes, all 8-bit absolute values. `pxrc_report_fixup` unconditionally replaces the descriptor. `pxrc_raw_event` rewrites report bytes using the cached alternating values. `pxrc_probe` allocates private state, parses, and starts hardware.

## Control flow
During parse, `pxrc_report_fixup` sets `*rsize` to the fixed descriptor length and returns the static descriptor. Probe stores zeroed private state in HID drvdata, parses the fixed descriptor, then starts HID normally. Each raw event alternates interpretation of `data[7]`: on one report it updates `dial`, on the next it updates `slider`. It then writes the cached slider to `data[1]` and cached dial to `data[7]`, toggles `alternate`, and allows generic HID input handling to continue.

## State and persistence behavior
Only the previous slider/dial values and the alternation bit persist between reports. They are reset on reconnect. There is no sysfs or device memory state.

## Dependencies and integration points
The file integrates with HID report descriptor fixup and raw-event mutation before generic joystick input processing. It depends on `hid-ids.h` for the PhoenixRC USB ID.

## Risks and test signals
Risks are unconditional descriptor replacement and reliance on strict report alternation. Dropped or reordered reports can temporarily pair stale slider/dial values. Tests should inspect the exposed eight axes, feed alternating raw reports, verify slider/dial stability, reconnect reset behavior, and generic joystick calibration in userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pxrc.c -->
