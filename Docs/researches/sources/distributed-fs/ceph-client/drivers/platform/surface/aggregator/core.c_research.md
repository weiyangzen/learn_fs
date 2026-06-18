# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/core.c

## Purpose

This source is the Surface Serial Hub serdev driver and module entry point for the Surface Aggregator subsystem. It binds the controller to the serial device, exposes a global controller reference, creates device links for clients, configures UART parameters from ACPI or defaults, implements sysfs firmware-version reporting, manages PM notifications, registers wake IRQs, and initializes shared caches/bus support.

## Important APIs, Types, And Functions

Important exports are `ssam_get_controller()`, `ssam_client_link()`, and `ssam_client_bind()`. Probe/remove logic lives in `ssam_serial_hub_probe()` and `ssam_serial_hub_remove()`. Serdev glue is `ssam_receive_buf()`, `ssam_write_wakeup()`, and `ssam_serdev_ops`. Setup helpers include ACPI CRS parsing, GPIO mapping, and `ssam_serdev_setup()`. PM callbacks include prepare/complete, suspend/resume, freeze/thaw, poweroff/restore, plus shutdown. Module setup uses `ssam_core_init()` and `ssam_core_exit()`.

## Control Flow

At `subsys_initcall`, the driver registers the optional bus, packet cache, event item cache, and serdev driver. Probe maps ACPI GPIOs, allocates and initializes the controller, opens/configures serdev, starts the controller, logs firmware version, sends D0-entry and display-on notifications, creates sysfs, sets up IRQ, publishes the global controller, and clears ACPI dependencies. Remove clears the global reference, frees IRQ/sysfs, removes clients, sends display-off/D0-exit notifications, shuts down the controller, closes serdev, and drops the controller reference.

## State And Persistence

State includes the global controller pointer under spinlock, serdev driver data, sysfs `sam/firmware_version`, wakeup capability, ACPI GPIO mappings, optional DT platform hub registration, and controller-owned state. No disk persistence exists. PM callbacks intentionally manipulate EC display/D0/event state across system sleep and hibernation.

## Dependencies And Integration Points

The file depends on ACPI, GPIO descriptors, OF, platform devices, PM, serdev, sysfs, units constants, Surface Aggregator public headers, local bus/controller headers, and tracepoint creation. It integrates with ACPI ID `MSHW0084` and OF compatible `microsoft,surface-sam`.

## Risks

The static controller model assumes a single provider. Wakeup is marked capable but disabled by default because wake event classification is incomplete. PM sequencing is firmware-sensitive: display-off/on and D0-exit/entry failures can leave EC event delivery impaired. The DT path registers a platform hub but does not store the returned platform device for later unregister in this file. `ssam_client_bind()` returns a controller pointer after dropping its own kref and relies on the device link for lifetime.

## Test Signals

Signals include serdev probe via ACPI and OF, UART parameter setup from ACPI CRS, firmware version sysfs reads, D0/display notification success on boot and PM, suspend/resume/hibernate cycles with keyboard/touchpad/battery events still working, client device removal before shutdown, IRQ setup and wake arm/disarm, module unload cleanup, and lockdep/kref checks around global controller access.
