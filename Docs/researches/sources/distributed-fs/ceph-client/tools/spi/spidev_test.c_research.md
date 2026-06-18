# sources/distributed-fs/ceph-client/tools/spi/spidev_test.c

Purpose: feature-rich spidev test utility for configuring SPI mode parameters and transferring default, escaped-string, file, or random buffers.

Important APIs, types, and functions: global options cover device, mode bits, speed, bits per word, delays, input/output files, transfer size, iterations, and verbosity. Functions include `hex_dump()`, `unescape()`, `transfer()`, `print_usage()`, `parse_opts()`, `transfer_escaped_string()`, `transfer_file()`, `show_transfer_rate()`, `transfer_buf()`, and `main()`. It uses `SPI_IOC_WR/RD_MODE32`, `SPI_IOC_WR/RD_BITS_PER_WORD`, `SPI_IOC_WR/RD_MAX_SPEED_HZ`, and `SPI_IOC_MESSAGE(1)`.

Control flow: `parse_opts()` maps short/long CLI options to mode flags such as CPHA/CPOL, loopback, dual/quad/octal, 3-wire, LSB-first, no-CS, ready, and MOSI idle. `main()` opens the device, writes and reads back mode/bits/speed, warns if the driver dropped requested mode bits, then selects one transfer path: escaped string (`-p`), input file (`-i`), random repeated buffers (`-S` with `-I`), or a built-in SD-card-like default sequence. `transfer()` builds `spi_ioc_transfer`, configures multi-lane tx/rx nbits, suppresses incompatible rx/tx buffers outside loopback, performs the ioctl, optionally writes received bytes to output file, and hex-dumps when verbose.

State and persistence: configuration globals hold the requested settings. `_read_count` and `_write_count` accumulate transfer-rate stats in random-buffer mode. Output file contents are persistent if `-o` is used; device configuration may persist according to spidev driver semantics.

Dependencies and integration points: depends on Linux spidev UAPI, getopt_long, and an SPI controller supporting the requested mode bits. It is built by `tools/spi/Makefile`.

Risks: many numeric options use `atoi()` without range validation. `iterations` defaults to zero, so `-S` without `-I` performs no transfers. `unescape()` assumes `\xNN` has two hex digits and advances four characters. Large input files allocate full-size tx/rx buffers. The code casts away `const` for rx pointer in `transfer()` but only writes through the kernel ioctl.

Test signals: readback prints the actual mode, bits, and speed. Loopback mode should validate random buffers and exit on mismatch. Verbose mode should dump TX/RX. Unsupported mode bits should produce the warning comparing requested and actual mode.
