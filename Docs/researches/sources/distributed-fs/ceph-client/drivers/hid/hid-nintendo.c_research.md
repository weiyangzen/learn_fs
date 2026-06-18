# sources/distributed-fs/ceph-client/drivers/hid/hid-nintendo.c

## Purpose

`hid-nintendo.c` is a full HID driver for Nintendo Switch Joy-Cons, Pro Controllers, charging grip combinations, and Nintendo Switch Online NES/SNES/Genesis/N64 controllers. It performs controller initialization through USB commands and Switch subcommands, reads calibration from controller SPI flash, exposes gamepad and optional IMU input devices, implements rumble, player/home LEDs, battery power-supply status, suspend/resume behavior, and careful subcommand rate limiting for Bluetooth reliability.

## Important APIs, Types, and Functions

- `struct joycon_ctlr` is the persistent controller object. It stores HID/input devices, player/home LEDs, controller state/type, spinlock, MAC address, synchronous command state, calibration data, battery data, rumble queue/workqueue, and IMU timestamp/average-delta state.
- Wire structs model reports: `joycon_subcmd_request`, `joycon_subcmd_reply`, `joycon_input_report`, `joycon_rumble_output`, and `joycon_imu_data`.
- Send path: `__joycon_hid_send()`, `joycon_hid_send_sync()`, `joycon_send_usb()`, `joycon_send_subcmd()`, `joycon_enforce_subcmd_rate()`, and `joycon_wait_for_input_report()`.
- Initialization helpers read info/calibration and enable modes: `joycon_read_info()`, `joycon_request_calibration()`, `joycon_request_imu_calibration()`, `joycon_set_report_mode()`, `joycon_enable_imu()`, `joycon_enable_rumble()`, and `joycon_init()`.
- Input path: `nintendo_hid_event()`, `joycon_ctlr_handle_event()`, `joycon_parse_report()`, stick/button/dpad reporters, and `joycon_parse_imu_report()`.
- FF path: rumble frequency/amplitude tables, `joycon_encode_rumble()`, `joycon_set_rumble()`, `joycon_send_rumble_data()`, and `joycon_rumble_worker()`.
- Device integration: `joycon_input_create()`, `joycon_imu_input_create()`, `joycon_leds_create()`, `joycon_power_supply_create()`, probe/remove, PM suspend/resume, and module init/exit for IDA cleanup.

## Control Flow

Probe allocates `joycon_ctlr`, initializes locks/waitqueue/workqueue, parses HID, marks the HID version high bit so userspace can distinguish this mapping, starts HIDRAW-only hardware, opens I/O, and calls `joycon_init()`. Initialization performs USB handshake and baud setup when applicable, requests controller info to determine real controller type, reads stick and IMU calibration with user calibration preferred over factory, enables IMU and rumble where supported, and switches to full input report mode. Probe then registers LEDs, battery power supply, main input device, optional IMU input device, and enters `JOYCON_CTLR_STATE_READ`.

Raw input first checks whether a synchronous USB/subcommand response is awaited. Matching replies are copied into `input_buf`, clear the message type, and wake the sender. Normal input reports are parsed only in READ state. Button/stick/dpad mapping depends on controller type, not only HID product ID. IMU reports contain three samples; the driver estimates sample timestamps from a running average of packet deltas and applies calibration before reporting accelerometer and gyro axes. Rumble is queued in a small circular buffer and sent by a workqueue, with periodic sends triggered by vibrator reports and rate limited to avoid Bluetooth drops.

## State and Persistence Behavior

State is per physical controller and mostly volatile. Calibration data read from controller SPI flash persists in the controller, while parsed calibration values persist in RAM. LEDs are represented by Linux LED class devices and mirrored to hardware by subcommands. Battery state is updated from input reports under spinlock. Rumble state persists in the queue and last encoded data packet; zero-rumble packets are sent a bounded number of times before traffic stops. Controller state gates command sending during removal and suspend.

## Dependencies and Integration Points

The driver integrates HID raw events/output reports, Linux input/FF, LED class, power-supply class, IDA player allocation, workqueues, waitqueues, mutexes, spinlocks, jiffies timing, PM callbacks, endian/unaligned helpers, and Nintendo IDs from `hid-ids.h`. It exposes HIDRAW rather than generic hid-input because the driver creates its own Linux input devices.

## Risks and Edge Cases

- Synchronous command matching depends on `output_mutex`, `msg_type`, and ACK IDs; unexpected replies can be treated as normal input or ignored.
- Bluetooth stability depends on timing heuristics and input-report cadence; regressions can cause disconnects.
- `joycon_input_create()` registers the input device before configuring capabilities, which is unusual and should be checked against input-core expectations in this tree.
- Rumble queue overwrite deliberately keeps the latest state but can drop intermediate effects.
- Calibration fallback allows operation but may produce inaccurate sticks/IMU.
- Removal destroys the workqueue after setting REMOVED, but any future LED/FF path must continue to handle `-ENODEV` cleanly.
- IMU timestamp estimation can be wrong under highly irregular host/controller packet timing.

## Test Signals

Test USB and Bluetooth probe paths, charging grip handshake failure, controller type decoding for NSO variants, SPI calibration reads with user/factory/default fallback, stick mapping bounds, button maps per controller type, IMU calibration/divisor zero handling, IMU dropped-packet compensation, rumble encoding and queue overrun, LED registration and set failures, battery properties, synchronous command timeout/retry, suspend/resume state transitions, and unplug during pending LED/rumble/subcommand work.
