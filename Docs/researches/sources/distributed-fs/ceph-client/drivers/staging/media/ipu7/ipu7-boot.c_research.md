# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.c

## Purpose

This file implements firmware boot/shutdown for IPU7 ISYS and PSYS microcontrollers, including boot config allocation, syscom queue memory setup, uC reset/start/stop, boot parameter register programming, and boot-state polling.

## Important APIs, Types, and Functions

Exported APIs are `ipu7_boot_init_boot_config()`, `ipu7_boot_release_boot_config()`, `ipu7_boot_start_fw()`, `ipu7_boot_stop_fw()`, and `ipu7_boot_get_boot_state()`. Internal helpers manage boot parameter register addresses, uC cell reset/start/stop/init, and common boot config initialization.

## Control Flow

`ipu7_boot_init_boot_config()` allocates DMA-visible boot config and queue memory, initializes version/frequency/syscom fields, aligns queue memory to 64 bytes, and fills host and firmware queue config views. `ipu7_boot_start_fw()` resets the uC, writes UNINIT/zero diagnostic registers/config DMA address, starts the cell, polls boot state until READY or critical, then records firmware queue-index MMIO address and message version. `ipu7_boot_stop_fw()` verifies READY, writes SHUTDOWN_CMD, polls INACTIVE or critical, and resets/stops the uC.

## State and Persistence Behavior

State is held on `struct ipu7_bus_device`: boot config CPU/DMA pointer, size, firmware entry, syscom queue memory, and queue indices pointer. These allocations persist between init and release.

## Dependencies and Integration Points

It integrates buttress registers, platform DMEM offsets, IPU7 DMA allocation/sync, syscom queue config, and firmware error logging.

## Risks and Edge Cases

If queue memory allocation fails after boot config allocation, callers rely on release cleanup. Boot and stop polling timeouts are finite. Critical boot states dump firmware logs and return errors. Boot register offsets differ by subsystem. DMA address truncation would be dangerous because boot registers are 32-bit firmware ABI addresses.

## Test Signals

Test boot READY path, critical state handling, boot timeout, shutdown INACTIVE path, queue index publication, queue memory alignment, and release cleanup after partial initialization failure.
