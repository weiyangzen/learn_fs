# sources/distributed-fs/ceph-client/tools/spi/spidev_fdx.c

Purpose: small spidev full-duplex/read utility for inspecting SPI device settings, issuing a two-transfer SPI message, and reading bytes.

Important APIs, types, and functions: functions are `do_read()`, `do_msg()`, `dumpstat()`, and `main()`. It uses `open()`, `read()`, `ioctl()`, `SPI_IOC_MESSAGE(2)`, `SPI_IOC_RD_MODE32`, `SPI_IOC_RD_LSB_FIRST`, `SPI_IOC_RD_BITS_PER_WORD`, and `SPI_IOC_RD_MAX_SPEED_HZ`.

Control flow: `main()` parses `-m N`, `-r N`, `-v`, and `-h`, requires one `/dev/spidevB.D` path, opens it read/write, prints current SPI settings with `dumpstat()`, optionally sends a two-part message where byte `0xaa` is transmitted before receiving `N` bytes, optionally performs a direct read of `N` bytes, then closes the device.

State and persistence: process state is limited to parsed counts and an unused `verbose` flag. It does not modify device mode or speed; it only reads settings and performs transfers. Buffers are fixed 32-byte stack arrays, and requested lengths are clamped.

Dependencies and integration points: depends on Linux spidev UAPI and a device node backed by an SPI controller/driver. Output is raw hex for simple manual inspection.

Risks: no mode setup means behavior depends entirely on prior device configuration. `do_msg()` transmits only one command byte and then receives into the same buffer; device protocols needing chip-select changes or more setup are unsupported. `verbose` is parsed but not used. Direct `read()` support depends on the spidev driver and target device behavior.

Test signals: `spidev_fdx /dev/spidevX.Y` should print settings. `-m` should show a response from `SPI_IOC_MESSAGE`; `-r` should show direct read bytes or a short-read diagnostic.
