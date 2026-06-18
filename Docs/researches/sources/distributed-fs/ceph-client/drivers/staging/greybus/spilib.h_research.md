# sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.h

## Purpose
Declares the public interface for the Greybus SPI library used by `spi.c` and potentially other Greybus SPI bridge wrappers.

## Important APIs and Types
`struct spilib_ops` optionally supplies `prepare_transfer_hardware()` and `unprepare_transfer_hardware()` callbacks operating on the parent `struct device`. `gb_spilib_master_init()` registers a Linux SPI controller over a Greybus connection, and `gb_spilib_master_exit()` tears it down.

## State, Dependencies, and Integration
The header forward-declares `struct device` and `struct gb_connection`, avoiding broad include dependencies. Persistent state is private to `spilib.c`; consumers only hold the Greybus connection and call init/exit.

## Risks and Test Signals
The interface risk is lifecycle symmetry: every successful `gb_spilib_master_init()` must be paired with `gb_spilib_master_exit()` before the Greybus connection is destroyed. Compile coverage should ensure users include this header without needing SPI internals.
