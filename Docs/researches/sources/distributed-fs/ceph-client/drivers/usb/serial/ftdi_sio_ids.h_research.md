# sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio_ids.h

## Purpose

This header is the FTDI USB-serial device identity catalog used by the FTDI SIO driver. It does not implement runtime behavior; instead it defines vendor IDs and product IDs for original FTDI chips, devices using FTDI's vendor ID, and third-party VID/PID pairs that should bind to the FTDI USB serial implementation. The file is intentionally broad because many products embed FTDI UART bridges while exposing product-specific IDs.

## Important APIs, Types, And Constants

The exported surface is a long set of `#define` constants. The central vendor constant is `FTDI_VID`, with canonical PIDs such as `FTDI_8U232AM_PID`, `FTDI_8U2232C_PID`, `FTDI_4232H_PID`, `FTDI_232H_PID`, `FTDI_FTX_PID`, and newer power-delivery or automotive variants. The rest of the header groups third-party products by vendor or device family: ELV, Matrix Orbital, Sealevel, Brainboxes, Papouch, RT Systems, Xsens, Actisense/Chetco, u-blox, and many others.

The header is consumed by `ftdi_sio.c`, where these names are used to populate `usb_device_id` match tables and sometimes to select per-device quirks. Some constants represent devices using FTDI's VID; others define both a vendor ID and one or more PIDs for a non-FTDI VID. Comments are part of the maintenance contract: they identify rebadged products, Windows-driver behavior, shared PIDs, future/reserved slots, or devices that emulate FTDI-compatible USB serial behavior.

## Control Flow

There is no local control flow. The effective flow is compile-time: include this header, expand constants into match table entries, and let the USB core compare connected descriptors against the table. When a descriptor matches, `ftdi_sio.c` performs probe, chip-family detection, endpoint setup, termios programming, and data path handling.

## State And Persistence

The file has no mutable state and no persistence. Its data affects kernel module alias generation and therefore which devices bind automatically. Changing a constant or adding a match changes persistent system behavior after the module is rebuilt and installed because hotplug/modprobe matching will see a different supported ID set.

## Dependencies And Integration Points

The header depends only on the C preprocessor and the consumers that include it. Its most important integration point is `ftdi_sio.c`. It also indirectly affects module metadata generated from the driver's `MODULE_DEVICE_TABLE`, distribution packaging of modaliases, and user expectations around whether a device appears as a ttyUSB port without manual binding.

## Risks

The main risk is incorrect binding. A wrong or overly broad VID/PID can attach the FTDI serial driver to a device interface that is not a UART bridge, or to a multi-interface product where only some interfaces are serial. Duplicate IDs can hide product-specific quirks if the consumer table orders entries incorrectly. Removing or renaming a constant can break table compilation. Because this is a large manually curated registry, numeric sorting and comment accuracy matter for reviewability. The `FTDI_BRICK_PID` entry deliberately supports counterfeit devices reprogrammed to PID zero; that compatibility choice has security and support implications because PID zero is not descriptive.

## Test Signals

Useful signals are compile coverage of `ftdi_sio.c`, module alias generation containing expected IDs, hotplug/probe tests for representative original FTDI devices and third-party IDs, regression checks for quirked devices with shared FTDI VID, and negative tests showing unrelated interfaces are not accidentally matched. Table-only changes should be reviewed against USB descriptor dumps and vendor documentation when available.
