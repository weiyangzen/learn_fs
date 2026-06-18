# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.c

## Purpose

`applespi.c` is the MacBook/MacBook Pro SPI keyboard and touchpad driver. It switches Apple ACPI-attached input hardware from USB to SPI when needed, exchanges fixed 256-byte SPI packets with keyboard, touchpad, and info endpoints, registers a keyboard input device immediately, and registers the multitouch touchpad after receiving model information from the controller.

## Important APIs, Types, and Functions

- Protocol structs model the hardware ABI: `keyboard_protocol`, `tp_finger`, `touchpad_protocol`, `touchpad_info_protocol`, command payloads, `message`, and `spi_packet`.
- `struct applespi_data` holds SPI messages/transfers, input devices, command queue state, last keyboard state, touchpad dimensions, ACPI GPE/method handles, LED state, drain/suspend flags, and debugfs state.
- `applespi_send_cmd_msg()` serializes touchpad-info, multitouch-init, caps-lock LED, and keyboard-backlight commands into one pending write exchange.
- `applespi_notify()` is the ACPI GPE handler and queues async reads; `applespi_async_read_complete()` and `applespi_got_data()` validate and dispatch received packets.
- `applespi_handle_keyboard_event()` reports rollover keyboard state; `report_tp_state()` reports multitouch slots and click state.
- `applespi_probe()`, `applespi_remove()`, `applespi_suspend()`, `applespi_resume()`, `applespi_shutdown()`, and `applespi_poweroff_late()` bind the SPI, ACPI, PM, LED, EFI, debugfs, and input lifecycles.

## Control Flow

Probe rejects systems where the USB interface is already active, allocates transfer buffers, caches ACPI `SIEN`/`SIST` handles, enables SPI, creates the keyboard input device, installs/enables the ACPI GPE handler, queues touchpad setup, registers a keyboard-backlight LED class device, and exposes debugfs touchpad-dimension helpers. GPE delivery calls `applespi_notify()`, which queues a read. The read callback CRC-checks the packet, reassembles up to two packets, validates the inner message CRC and declared length, then dispatches keyboard reads, touchpad reads, or write responses. Write commands are serialized under `cmd_msg_lock`; completion reads a four-byte status and waits for the response GPE before allowing the next command.

## State and Persistence Behavior

Runtime state is mostly in `applespi_data`: last pressed keys and Fn state are retained to generate releases, touchpad slot positions persist between reports for input-mt assignment, `saved_msg_len` tracks multipart assembly, and desired/actual LED/backlight command state is held until hardware catches up. The driver persists keyboard backlight level through the EFI variable `KeyboardBacklightLevel`. Suspend/remove set drain flags, wait for active writes/reads, disable GPEs, and mark the device suspended; resume clears transient command/read/write state, re-enables SPI/GPE, and reinitializes multitouch mode.

## Dependencies and Integration Points

The driver integrates with SPI core async transfers, ACPI methods and GPEs (`APP000D`, `_GPE`, `SIEN`, `SIST`, optional USB-status methods), Linux input and multitouch, LED class, EFI runtime variables, debugfs, CRC16, unaligned helpers, and local `applespi.h`/`applespi_trace.h`. It uses module parameters for Fn behavior, ISO key swapping, Fn remapping, and touchpad dimensions.

## Risks and Edge Cases

The protocol parser depends on exact packet/message length, CRC, endian, and maximum-packet assumptions; malformed offsets or finger counts can otherwise corrupt message assembly or input reporting. Command writes are single-flight with a timeout heuristic, so lost response GPEs can delay LED/backlight updates. Touchpad registration runs from workqueue because SPI callbacks cannot sleep; events before registration are dropped. The touchpad model table has fallback dimensions for unknown models. The driver reads ACPI buffer properties as `u64 *`, so malformed firmware property sizes would be risky. Drain and suspend ordering must avoid deadlocks between callbacks, GPE completion, and `cmd_msg_lock`.

## Test Signals

Useful signals include probe on APP000D systems with USB disabled/enabled, ACPI method failures, GPE read storms, corrupted packet CRC/length/offset handling, two-packet touchpad reports, keyboard rollover overflow, Fn mode/remap/ISO translation, caps-lock LED events, backlight scaling and EFI save/restore, unknown touchpad models and dimension overrides, suspend/resume with in-flight reads or writes, remove during active GPEs, and tracepoint output for reads/writes/status/CRC failures.
