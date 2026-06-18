# sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c` is a legacy `/dev/watchdog` miscdevice driver for Acquire single-board computer watchdog hardware controlled by two x86 I/O ports. It starts or pings the timer by reading one port and stops it by reading another. The complete 328-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_stop`, `wdt_start`, and `nowayout`. Runtime helpers are `acq_keepalive()` and `acq_stop()`. File operations are `acq_write()`, `acq_ioctl()`, `acq_open()`, and `acq_close()` with `compat_ptr_ioctl`. Platform lifecycle functions are `acq_probe()`, `acq_remove()`, `acq_shutdown()`, `acq_init()`, and `acq_exit()`. State variables include `acq_platform_device`, `acq_is_open`, and `expect_close`.

## Control Flow

Module init creates a synthetic platform device and probes `acquirewdt_driver`. Probe reserves the stop and start I/O regions and registers a miscdevice on `WATCHDOG_MINOR`. Opening `/dev/watchdog` enforces single-open via `test_and_set_bit()`, optionally pins the module for nowayout, and starts the hardware with `acq_keepalive()`. Writes scan for magic close character `V` when nowayout is false and always ping on nonzero writes. Ioctls expose support, status, enable/disable, keepalive, and a fixed unknown timeout value of `0`. Release stops only after a magic close; otherwise it logs a critical warning and pings again. Shutdown stops the watchdog on soft shutdown.

## State and Persistence Behavior

The driver stores only process-open state and the magic-close flag. Hardware state persists in the board watchdog until refreshed, stopped, or timeout reset occurs. The actual timeout is jumper-selected and not discoverable by the driver.

## Dependencies and Integration Points

It depends on `HAS_IOPORT` style x86 port access (`inb_p()`), platform device/driver plumbing, miscdevice registration, watchdog ioctl constants, and userspace `/dev/watchdog` ABI expectations. It is selected by `CONFIG_ACQUIRE_WDT` and built as `acquirewdt.o`.

## Risks and Edge Cases

The hardware cannot be probed safely, so wrong module parameters can read unrelated I/O ports. `WATCHDOG_HEARTBEAT` is reported as zero because the hardware timeout is jumper-defined. The legacy miscdevice path lacks watchdog-core conveniences such as automatic device-managed registration, sysfs reporting, and framework-managed boot-running handling. Unexpected close deliberately leaves the watchdog armed.

## Test Signals

Check I/O region reservation failure handling, single-open behavior, magic close and nowayout behavior, `WDIOC_SETOPTIONS`, `WDIOC_KEEPALIVE`, reported timeout, platform remove cleanup, and shutdown stop behavior on target hardware or an I/O-port emulator.
