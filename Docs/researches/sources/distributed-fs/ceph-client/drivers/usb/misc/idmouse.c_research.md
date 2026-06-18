# sources/distributed-fs/ceph-client/drivers/usb/misc/idmouse.c

Purpose: Character driver for Siemens/Cherry ID Mouse FingerTIP fingerprint sensors. It captures one grayscale PGM fingerprint image at open time and serves that image via read from `/dev/idmouse%d`.

Important APIs and types: `struct usb_idmouse`, `idmouse_create_image()`, `idmouse_open()`, `idmouse_read()`, `idmouse_release()`, `idmouse_probe()`, and vendor `FTIP_*` control commands. It registers a USB class device at minor base 132 and uses autosuspend around image capture.

Control flow: probe binds only the data interface (`bInterfaceClass == 0x0A`), finds a bulk-IN endpoint, allocates a buffer large enough for the PGM image plus bulk transfer headroom, and registers the char device. Open is exclusive, wakes the device, runs a command sequence to acquire/reset the sensor, bulk-reads until the full image size, validates expected black/right and white/bottom borders, then stores the image in the device buffer. Reads use `simple_read_from_buffer()` over the captured image.

State and persistence: `bulk_in_buffer` holds the latest captured image for the open file; open/present flags are mutex protected. Disconnect deregisters the node and defers freeing if open. Risks include long blocking capture in open, heuristic image validation returning `-EAGAIN`, no retry loop in kernel, no URB cancellation because bulk reads are synchronous, and legacy sensor command assumptions. Test signals include capture success with known image borders, open exclusivity, partial read offsets, autosuspend get/put, disconnect while open, and fallback from 0x200 packet size to original endpoint size.
