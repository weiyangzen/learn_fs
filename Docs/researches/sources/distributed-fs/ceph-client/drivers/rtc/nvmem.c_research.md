# sources/distributed-fs/ceph-client/drivers/rtc/nvmem.c

## Purpose

`nvmem.c` is the RTC subsystem bridge for drivers that expose battery-backed RAM or EEPROM through the generic NVMEM framework. It provides one helper, `devm_rtc_nvmem_register()`, that lets an RTC driver register an NVMEM device tied to the RTC parent device and module owner.

## Important APIs, types, and functions

`devm_rtc_nvmem_register(struct rtc_device *rtc, struct nvmem_config *nvmem_config)` fills `nvmem_config->dev` with `rtc->dev.parent`, copies `rtc->owner`, enables `add_legacy_fixed_of_cells`, and calls `devm_nvmem_register()`. It returns `0`, a negative errno, or `-ENODEV` when no config is supplied.

## Control flow

The helper is linear: validate config, populate ownership and device fields, register with NVMEM, log an error if registration fails, and return `PTR_ERR_OR_ZERO()`.

## State and persistence behavior

This file does not manage storage itself. Persistence is provided by the underlying RTC hardware and the driver-supplied `reg_read` and `reg_write` callbacks in `struct nvmem_config`. Registration is devres-managed, so the NVMEM device is released with the parent.

## Dependencies and integration points

It depends on `linux/nvmem-consumer.h`, `linux/rtc.h`, `linux/err.h`, and `linux/types.h`. Drivers such as `rtc-abx80x.c` integrate by building an NVMEM config for SRAM and passing their `struct rtc_device`.

## Risks and edge cases

The helper mutates the caller's config, so drivers should not reuse the same static config across incompatible devices without care. NVMEM access semantics, locking, and bounds are entirely the responsibility of the driver's callbacks. Missing `nvmem_config` returns `-ENODEV`, which callers should treat as setup failure only if NVMEM is required.

## Test signals

Probe a driver with RTC-backed NVMEM and confirm `/sys/bus/nvmem/devices` appears, legacy fixed OF cells are available, reads and writes use the RTC parent device, module unload or device removal tears down the NVMEM device, and callback errors propagate to userspace.
