# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tiny-usb.c

## Purpose

`i2c-tiny-usb.c` exposes the external i2c-tiny-usb USB adapter as a Linux `i2c_adapter`. The hardware protocol is simple vendor USB control messages whose command IDs mirror firmware commands for echo/function query, delay setup, I2C I/O, and status reporting.

## Important APIs, Types, and Functions

The main state is `struct i2c_tiny_usb`, holding the USB device/interface and embedded adapter. `usb_xfer()` implements `struct i2c_algorithm.xfer`, and `usb_func()` queries firmware functionality through `CMD_GET_FUNC`. `usb_read()` and `usb_write()` wrap `usb_control_msg()` with temporary DMA-safe buffers. Probe and disconnect are handled by `i2c_tiny_usb_probe()` and `i2c_tiny_usb_disconnect()` in a `usb_driver`.

## Control Flow

Probe rejects non-vendor interface associations, allocates state, stores it with `usb_set_intfdata()`, configures adapter metadata, sends `CMD_SET_DELAY`, and registers the adapter. Transfers iterate each `i2c_msg`, add begin/end bits to the command for the first/last message, perform a USB control read or write, then query one status byte. Address NAK becomes `-ENXIO`; short USB transfers become `-EIO`; success returns the number of messages completed.

## State and Persistence Behavior

The module parameter `delay` is written to firmware at probe and persists in the attached adapter until changed by reset/reprobe. No transfer cache exists. Adapter state is tied to USB interface lifetime. The quirk `I2C_AQ_NO_ZERO_LEN_READ` prevents invalid zero-length control reads.

## Dependencies and Integration Points

The driver depends on USB core, Linux I2C core, vendor-specific USB IDs, and firmware command compatibility. It advertises `I2C_CLASS_HWMON` and uses `algo_data` to connect the adapter to the USB state.

## Risks

USB short transfers are treated as hard I/O failures, but `usb_read()` copies the full requested length from the DMA buffer even when the control transfer returned short or negative. Firmware status semantics are narrow: only address NAK is distinguished from other statuses. Probe ignores the return value of `i2c_add_adapter()`, so registration failure would still log a successful connection.

## Test Signals

Useful signals include USB probe with supported VID/PID, successful delay setup, `i2cdetect` visibility, read/write message sequences with repeated start begin/end flags, NAK propagation as `-ENXIO`, zero-length read rejection by adapter quirks, and clean disconnect with adapter removal.
