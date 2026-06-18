# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-platform.c

## Purpose

`arche-platform.c` is the parent Arche platform driver. It controls SVC reset/sysboot/reference clock, populates child APB devices, manages wake-detect IRQ sequencing, coordinates system suspend/resume behavior, and registers the APB controller driver.

## Important APIs, Types, and Functions

Core state is `struct arche_platform_drvdata`, containing SVC GPIOs, clock, wake-detect IRQ state, locks, PM notifier, child count, and current platform state. Important helpers are `arche_platform_coldboot_seq()`, `arche_platform_fw_flashing_seq()`, `arche_platform_poweroff_seq()`, wake-detect IRQ handlers, `apb_cold_boot()`, `apb_poweroff()`, sysfs `state` handlers, and the PM notifier. Module init registers this platform driver and then `arche_apb_init()`.

## Control Flow

Probe requests SVC reset/sysboot/refclk/wake-detect resources, initializes locks, requests a threaded IRQ on wake-detect rising/falling edges, creates sysfs `state`, populates APB child nodes, registers a PM notifier, and cold-boots unless `arche,init-off` is set. A long wake-detect low pulse followed by rising edge schedules the threaded handler, which powers off APBs, cold-boots them, enables the USB3613 hub path, and resets wake state. Sysfs state writes power off APBs before parent state transitions, except firmware-flashing mode leaves APBs to user choice.

## State and Persistence Behavior

The parent stores volatile platform and wake-detect state in memory. Hardware state is reflected in SVC reset/sysboot GPIOs, SVC reference clock, APB child power, wake IRQ enablement, and optional USB3613 hub mode. No persistent storage is used.

## Dependencies and Integration Points

It depends on gpiod, clocks, OF platform population, IRQ threading, PM notifiers, Greybus headers, optional USB3613 hub control, and child APB exported functions in `arche_platform.h`.

## Risks and Edge Cases

`arche_platform_pm_notifier()` returns `NOTIFY_STOP` when suspend is requested outside active state, which can block system suspend unexpectedly. `gb_platform_poweroff_seq()` disables IRQ only outside firmware-flashing, so IRQ state needs careful transition testing. Wake-detect state uses spinlock while platform state uses mutex; ordering must stay consistent. `arche_platform_remove()` calls poweroff without taking `platform_state_mutex`, unlike sysfs and PM paths. Error paths after child population need to unwind children, sysfs, PM notifier, and clocks exactly once.

## Test Signals

Validate boot with and without `arche,init-off`, wake-detect short and long pulses, concurrent sysfs and IRQ transitions, suspend/resume notifier behavior, child APB failure handling, USB3613 present/absent builds, remove/shutdown, and OF child population rollback.
