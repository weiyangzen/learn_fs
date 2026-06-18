# sources/distributed-fs/ceph-client/include/linux/usb/usbio.h

## Purpose
This header defines Intel USBIO packet formats, client names, quirks, GPIO/I2C commands, descriptors, and auxiliary-bus helper APIs for USB-attached GPIO and I2C functions.

## Important APIs, types, and functions
Key constants are `USBIO_GPIO_CLIENT`, `USBIO_I2C_CLIENT`, `USBIO_QUIRK_*`, packet type IDs, GPIO/I2C commands, bank/bus limits, and pin/config bit helpers. Important packed types are `usbio_packet_header`, `usbio_ctrl_packet`, `usbio_bulk_packet`, GPIO bank/init/rw descriptors, and I2C bus/init/rw descriptors. APIs include `usbio_control_msg()`, `usbio_bulk_msg()`, acquire/release, buffer-length/quirk queries, and ACPI binding.

## Control flow, state, and persistence
Auxiliary child drivers acquire the shared USBIO parent, send typed control or bulk command packets, then release it. GPIO/I2C operations encode bank, pin, bus, config, speed, and payload lengths into packed little-endian messages. Quirks alter transfer lengths, initialization ACK behavior, and speed limits. State is runtime device arbitration and controller configuration; ACPI IDs provide firmware binding.

## Dependencies and integration points
It depends on auxiliary bus, endian types, list/types, and ACPI identifiers. It integrates USBIO parent drivers with GPIO and I2C auxiliary clients.

## Risks and test signals
Risks include counted flexible-array length mismatches, quirk-dependent transfer splitting, concurrent client access without acquire/release, and endian mistakes in I2C/GPIO payloads. Tests should cover control and bulk packets, max buffer limits, every quirk flag, ACPI matching, and invalid bus/bank/pin values.
