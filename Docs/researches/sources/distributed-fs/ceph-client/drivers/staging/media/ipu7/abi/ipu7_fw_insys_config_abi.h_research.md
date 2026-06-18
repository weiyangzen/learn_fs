# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_insys_config_abi.h

## Purpose

This header defines the ISYS firmware subsystem configuration block passed in boot config to the input-system firmware.

## Important APIs, Types, and Functions

`struct ipu7_insys_config` contains `timeout_val_ms`, `ia_gofo_logger_config`, and `ipu7_wdt_abi`. It includes boot, common config, and ISYS ABI headers.

## Control Flow

No executable flow. `ipu7_fw_isys_init()` allocates this structure through IPU7 DMA, zeros it, configures syscom logging and watchdogs, syncs it, and passes its DMA address to `ipu7_boot_init_boot_config()`.

## State and Persistence Behavior

The structure is persistent DMA memory while ISYS firmware is initialized and is freed by `ipu7_fw_isys_release()`.

## Dependencies and Integration Points

It bridges boot config and ISYS firmware command queues, specifically logger and watchdog setup.

## Risks and Edge Cases

Firmware interprets exact field layout. The current driver leaves timeout and watchdogs disabled/zeroed, so firmware-side timeout behavior depends on firmware defaults or disabled watchdog policy.

## Test Signals

ISYS boot with syscom logging enabled, DMA sync verification, and firmware log queue output are useful signals.
