# sources/distributed-fs/ceph-client/drivers/iio/adc/viperboard_adc.c

## Purpose
This file implements the Nano River Technologies Viperboard ADC IIO child driver. It exposes four direct voltage input channels backed by USB control messages through the parent Viperboard MFD device.

## Important APIs, Types, And Functions
`struct vprbrd_adc_msg` is the packed three-byte protocol frame containing command, channel, and returned value. `struct vprbrd_adc` stores a pointer to the parent `struct vprbrd`, which supplies the USB device, shared transfer buffer, timeout, request IDs, and parent mutex. `vprbrd_iio_read_raw()` is the only IIO data path. `vprbrd_adc_probe()` allocates the IIO device and wires the four `IIO_VOLTAGE` raw-only channel specs.

## Control Flow
Probe retrieves the parent MFD state from `pdev->dev.parent`, allocates private IIO state, points it at the parent, sets `INDIO_DIRECT_MODE`, and registers the device. On `IIO_CHAN_INFO_RAW`, the read callback locks the parent Viperboard mutex, fills the shared buffer with `VPRBRD_ADC_CMD_GET` and the requested channel, sends it via a USB vendor control OUT request, receives the response via a control IN request, copies `admsg->val` to `*val`, unlocks, and returns `IIO_VAL_INT` if both transfers returned the exact expected frame size.

## State And Persistence
The ADC child has almost no private state beyond the parent pointer. It uses the parent's shared USB buffer and lock, so ADC transfers are serialized with other parent users. There is no persistent calibration, scale, or sample-rate state.

## Dependencies And Integration Points
The driver depends on the Viperboard MFD core, USB control-message helpers, platform-device child creation, and the IIO core. Its userspace ABI is four raw voltage channels. It registers as `platform:viperboard-adc` and depends on the parent exposing valid `VPRBRD_USB_REQUEST_ADC`, USB type constants, timeout, lock, and buffer.

## Risks And Test Signals
The result is only 8 bits (`u8 val`) and no scale is exposed, so consumers need board knowledge for engineering units. Both USB transfers must return exactly three bytes; short transfers map to `-EREMOTEIO`. The read callback assigns `*val` before checking the receive length, but still returns an error on failure. Tests should cover all four channels, parent lock contention, disconnect or stalled USB control transfers, short IN/OUT transfers, and repeated reads under concurrent MFD child activity.
