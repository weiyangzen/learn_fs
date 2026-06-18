# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_config_abi.h

## Purpose

This small ABI header defines common firmware configuration values for watchdog and command timers.

## Important APIs, Types, and Functions

It defines `IPU_CONFIG_ABI_WDT_TIMER_DISABLED`, `IPU_CONFIG_ABI_CMD_TIMER_DISABLED`, and `struct ipu7_wdt_abi` with `wdt_timer1_us` and `wdt_timer2_us`.

## Control Flow

No runtime control flow is present. Subsystem config structures embed `ipu7_wdt_abi`, and setup code fills the fields before synchronizing DMA-visible config memory.

## State and Persistence Behavior

The watchdog fields become part of DMA-visible subsystem configuration passed to firmware at boot.

## Dependencies and Integration Points

It includes Linux types and is included by ISYS/PSYS config ABI headers.

## Risks and Edge Cases

Zero disables watchdog timers in current users. Changing defaults can alter firmware hang detection and recovery behavior.

## Test Signals

Boot firmware with disabled and non-disabled watchdog values where supported; inspect config DMA buffer before boot.
