# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bcm203x.c

## Purpose

`bcm203x.c` is a firmware loader for Broadcom Blutonium BCM2033 USB Bluetooth devices. It loads a mini driver, selects controller memory, streams the main firmware, checks completion, and then exits so the device can operate with its loaded firmware.

## Important APIs, Types, And Functions

`bcm203x_table` matches USB device `0x0a5c:0x2033`. `struct bcm203x_data` stores the USB device, loader state, delayed work, shutdown flag, single URB, transfer buffer, copied firmware bytes, firmware size, and sent offset. State constants cover `BCM203X_LOAD_MINIDRV`, `SELECT_MEMORY`, `CHECK_MEMORY`, `LOAD_FIRMWARE`, `CHECK_FIRMWARE`, `RESET`, and `ERROR`.

`bcm203x_complete` is the URB completion state machine. `bcm203x_work` submits the URB from process context after deliberate small delays. `bcm203x_probe` allocates state, requests `BCM2033-MD.hex` and `BCM2033-FW.bin`, prepares the initial bulk URB, stores interface data, and schedules work. `bcm203x_disconnect` stops work, kills the URB, and frees firmware/buffer state.

## Control Flow

Probe only handles interface 0. It allocates one URB and a buffer sized for the larger of mini-driver size and 4096 bytes, copies mini-driver data into that buffer, fills a bulk URB to OUT endpoint `0x02`, then loads and copies the main firmware into private memory. Completion of the mini-driver bulk write sends `#` to select memory, then schedules work. The subsequent interrupt read from IN endpoint `0x81` expects `#`; if present, firmware chunks of up to 4096 bytes are bulk-written until complete. Then an interrupt read expects `.` to confirm firmware load. Any URB status or unexpected marker moves to error state.

## State And Persistence

The state machine is stored in `data->state`; firmware bytes are copied because the firmware object is released during probe. The driver does not register an HCI device and keeps no persistent host-side state after disconnect. Device firmware state persists in the controller until reset or power loss.

## Dependencies And Integration Points

The driver uses USB bulk and interrupt URBs, the firmware loader, kernel workqueues, and Bluetooth logging. Kconfig selects `FW_LOADER` for `BT_HCIBCM203X`, and the module declares both firmware names.

## Risks

The state machine relies on a single reusable URB and buffer, so completion and disconnect ordering must remain strict. `bcm203x_disconnect` assumes interface data is present and kills the URB after setting shutdown and cancelling work. Any change that releases firmware memory before copying would be invalid because the main firmware is sent asynchronously after probe returns. Error states log failures but do not retry. Endpoint addresses are hard-coded, so this is intentionally specific to the Blutonium loader interface.

## Test Signals

Useful signals are successful requests for both firmware files, expected `#` and `.` handshakes, no URB status errors, clean disconnect during active load, and final device usability by the Bluetooth stack. Negative tests should cover missing mini-driver, missing firmware, short memory-select response, and USB unplug during scheduled work.
