# sources/distributed-fs/ceph-client/drivers/spi/spidev.c

## Purpose

`spidev.c` implements the generic userspace character-device interface for selected SPI devices. It exposes `/dev/spidevB.C` nodes backed by the SPI core so applications can issue simple read/write half-duplex transfers or full `SPI_IOC_MESSAGE()` transfer arrays without a dedicated kernel protocol driver.

## Important APIs, Types, And Functions

`struct spidev_data` tracks the character device number, per-device SPI lock, underlying `struct spi_device *`, list linkage, open-user count, open-time TX/RX bounce buffers, and current speed override. Global state includes the reserved major `153`, `N_SPI_MINORS`, the `minors` bitmap, `device_list`, `device_list_lock`, and module parameter `bufsiz`.

File operations are `spidev_read()`, `spidev_write()`, `spidev_ioctl()`, optional `spidev_compat_ioctl()`, `spidev_open()`, and `spidev_release()`. Transfer helpers are `spidev_sync_unlocked()`, `spidev_sync_write()`, `spidev_sync_read()`, `spidev_message()`, and `spidev_get_ioc_message()`. Driver lifecycle uses `spidev_probe()`, `spidev_remove()`, `spidev_init()`, and `spidev_exit()`.

## Control Flow And State

Module init registers the character major, registers the `spidev` class, and registers an SPI driver with explicit SPI IDs, OF compatible strings, and development-only ACPI IDs. Probe rejects direct `"spidev"` DT compatibles through `spidev_of_check()`, allocates `spidev_data`, finds a free minor, creates a device node named from controller bus and chip select, links the instance into `device_list`, records the default speed, and stores driver data on the SPI device.

Open locates the `spidev_data` by device number under `device_list_lock`, lazily allocates one TX and one RX bounce buffer of `bufsiz`, increments the user count, and stores the object in `file->private_data`. Read and write reject requests larger than `bufsiz`, lock `spi_lock`, check whether remove has nulled `spidev->spi`, and run a single SPI transfer using the bounce buffer. `SPI_IOC_MESSAGE()` copies a user transfer array, builds a kernel `spi_message`, allocates aligned slices from the bounce buffers for each TX/RX transfer, copies TX data from userspace, calls `spi_sync()`, then copies RX data back.

IOCTL mode writes save old state, mutate `spi->mode`, `bits_per_word`, or `max_speed_hz`, call `spi_setup()`, and restore on failure. Speed writes store a per-file-interface speed in `spidev->speed_hz` while restoring `spi->max_speed_hz` to the original controller-facing value after setup. Remove prevents new opens by unlinking from `device_list`, sets `spidev->spi = NULL` under `spi_lock` so existing descriptors return `-ESHUTDOWN`, destroys the device node, frees the minor, and frees the object only when no file descriptors remain.

## State And Persistence Behavior

No settings are persistent across driver unbind or reboot. Runtime mode changes modify the underlying `spi_device` while the device exists. Bounce buffers exist only while at least one descriptor is open. Minor numbers are reused dynamically and depend on probe order; udev or mdev is expected to create/remove nodes from class events.

## Dependencies And Integration Points

This file depends on the SPI core API (`spi_sync()`, `spi_setup()`, `spi_target_abort()` in target builds), Linux character-device registration, device classes, user-copy helpers, compat pointer conversion, module parameters, and firmware matching tables. It intentionally limits production DT use to hardware-specific compatible strings and warns for generic development ACPI IDs.

## Risks And Test Signals

Risks include exposing raw bus access that can disrupt other devices through mode changes such as `SPI_CS_HIGH`, `SPI_NO_CS`, or three-wire settings; incorrect userspace transfer sizes causing buffer overflow if `bufsiz` accounting regresses; removal races with active file descriptors; and compat ioctl pointer truncation mistakes. Useful tests are repeated open/close with lazy buffer allocation, read/write and multi-transfer ioctl paths, `bufsiz` overflow rejection, mode/speed/bits setup rollback on controller rejection, device removal while descriptors are active, minor exhaustion, compat `SPI_IOC_MESSAGE()`, and target-mode release abort behavior.
