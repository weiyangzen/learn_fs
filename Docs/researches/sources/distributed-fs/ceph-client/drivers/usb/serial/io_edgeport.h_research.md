# sources/distributed-fs/ceph-client/drivers/usb/serial/io_edgeport.h

## Purpose

This header defines the Linux-visible Edgeport product information structure and small helper macros needed by the Inside Out Networks Edgeport driver. It connects USB vendor/product descriptor data, boot/firmware version fields, hardware capability flags, and EPiC compatibility bits into one structure used by `io_edgeport.c`.

## Important APIs, Types, And Constants

`MAX_RS232_PORTS` defines the maximum number of RS-232 ports per Edgeport device as eight. `LOW8` and `HIGH8` extract byte halves of a 16-bit value and are used when building UART divisor commands. The header includes `io_usbvend.h`, which provides USB vendor IDs, Edgeport product IDs, descriptor layouts, firmware download constants, and `struct edge_compatibility_bits`.

The main type is `struct edgeport_product_info`. It contains product ID, number of ports, product-info version, RS-232/RS-422/RS-485/server bitfields, ROM/RAM size, CPU and board revision, boot firmware version, operational firmware version, manufacturing descriptor date, hardware type, selected firmware download file, EPiC spec version, and EPiC compatibility bits.

## Control Flow

There is no local control flow. `io_edgeport.c` fills `edgeport_product_info` either from classic manufacturing and boot descriptors or from an EPiC compatibility descriptor. Later paths inspect fields such as `NumPorts`, `iDownloadFile`, `Firmware*`, and `Epic` capability bits to decide firmware loading, EEPROM update behavior, command support, and debug reporting.

## State And Persistence

The header has no state. Instances of `struct edgeport_product_info` live in `struct edgeport_serial` and persist for the attached device lifetime. The values mirror device descriptors and firmware metadata; they are not independently persisted by the host, although firmware/ROM update paths may alter the device's persistent boot image.

## Dependencies And Integration Points

The header depends on Linux integer types and `io_usbvend.h`. It is part of a three-header contract with `io_ionsp.h` and `io_16654.h`: product metadata here, IOSP framing in `io_ionsp.h`, and UART register definitions in `io_16654.h`. `io_edgeport.c` relies on the exact layout to copy descriptor fields and print product information.

## Risks

The bitfield layout and mixed endian fields must match the assumptions in the driver and firmware descriptors. Misinterpreting `iDownloadFile` can select the wrong firmware image. Incorrect `NumPorts` or compatibility bits can make the driver allocate the wrong number of ports or send unsupported IOSP commands. Because this structure is populated from device-provided data, callers must continue to treat values as descriptors that can be malformed or inconsistent with USB core expectations.

## Test Signals

Signals include descriptor parsing for classic and EPiC devices, correct firmware image selection for I930 versus 80251 hardware, correct RS-232/RS-422/RS-485 flag reporting, version logging, compatibility-bit gating of IOSP commands, and warning behavior when descriptor port count disagrees with the USB serial driver's configured port count.
