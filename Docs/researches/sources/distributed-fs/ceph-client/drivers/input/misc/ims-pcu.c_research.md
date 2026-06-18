<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c

## Purpose
`ims-pcu.c` is a USB driver for IMS Passenger Control Unit devices. In application mode it creates button and optional gamepad input devices plus a keyboard-backlight LED; in bootloader mode it can request and flash Intel HEX firmware. It also exposes sysfs attributes for device identity, reset, firmware update, firmware status, and OFN sensor configuration.

## Important APIs, Types, and Functions
`struct ims_pcu` is the main state container: USB device/interfaces/endpoints/URBs, protocol framing buffers, command/response completions, firmware address range, sysfs-visible identity strings, LED/input subdevices, and mode flags. Input setup is split across `ims_pcu_setup_buttons()`, `ims_pcu_setup_gamepad()`, and report helpers. The byte-stuffed packet protocol is handled by `ims_pcu_process_data()`, `ims_pcu_send_command()`, `__ims_pcu_execute_command()`, and bootloader wrappers. Firmware flashing uses `request_ihex_firmware()`, `ihex_validate_fw()`, `ims_pcu_flash_firmware()`, and `ims_pcu_verify_block()`. USB lifecycle is handled by `ims_pcu_probe()`, `ims_pcu_disconnect()`, `ims_pcu_suspend()`, and `ims_pcu_resume()`.

## Control Flow
Probe allocates state, detects application versus bootloader from USB ID, parses the CDC union to locate control/data interfaces and endpoints, claims the data interface, allocates URBs/buffers, submits interrupt and bulk IN URBs, sets CDC line coding/state, and then initializes mode-specific features. Application mode queries identity, firmware/bootloader versions, reset reason, device ID, registers LED, buttons, and optional gamepad, then sets `setup_complete` so unsolicited button packets are reported. Bootloader mode queries flash bounds and starts an asynchronous firmware request. Disconnect from the control interface stops I/O, tears down mode-specific resources, frees buffers, and frees state.

## State and Persistence Behavior
Command state is serialized by `cmd_mutex` and matched by response type plus `ack_id`. Packet receive state tracks STX/DLE/checksum and is reset after ETX. Device identity strings are cached and can be updated through sysfs using `SET_INFO`. Firmware update status is a percentage or error code. `setup_complete` gates event reporting during teardown, with a memory barrier before input destruction.

## Dependencies and Integration Points
The driver integrates with USB CDC descriptors, USB core interface claiming, URBs, input, LED class, firmware loader, Intel HEX parser, sysfs attribute groups, unaligned helpers, and PM callbacks. User space sees evdev devices, LED class device `pcuN::kbd_backlight`, and USB-interface sysfs controls.

## Risks and Test Signals
Risks include complex protocol framing/chunking, command timeouts, response ID wrap rules, firmware address correction (`addr / 2`), bootloader disconnect/reconnect flow, sysfs writes racing with disconnect, and a notable cleanup risk where `ims_pcu_buffers_free()` frees `urb_in_buf` using `max_out_size` instead of `max_in_size`. Tests should cover packet escaping/checksum, unsolicited button/gamepad reports, command completion matching, CDC descriptor validation, firmware flashing/verify failure cases, sysfs visibility in both modes, suspend/resume URB restart, and disconnect during async firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c -->
