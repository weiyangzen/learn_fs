# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi.h

## Purpose
`gpiolib-acpi.h` is the internal ACPI GPIO interface shared by gpiolib core code and ACPI-specific implementation files. It declares gpiochip lifecycle hooks, ACPI descriptor lookup and counting helpers, deferred IRQ helpers, boot-event policy helpers, and ignore-list helpers.

## Important APIs, Types, And Functions
When `CONFIG_ACPI` is enabled, it declares `acpi_gpiochip_add()`, `acpi_gpiochip_remove()`, `acpi_gpiochip_request_interrupts()`, `acpi_gpiochip_free_interrupts()`, `acpi_find_gpio()`, and `acpi_gpio_count()`. Without ACPI, inline stubs either no-op or return `-ENOENT`/`-ENODEV`.

The header also declares `acpi_gpio_process_deferred_list()`, `acpi_gpio_add_to_deferred_list()`, `acpi_gpio_remove_from_deferred_list()`, `acpi_gpio_need_run_edge_events_on_boot()`, `enum acpi_gpio_ignore_list`, and `acpi_gpio_in_ignore_list()` for coordination between ACPI core and quirks code.

## Control Flow
Including code can call the same API regardless of build configuration. The compile-time branch keeps non-ACPI builds from needing ACPI implementation objects while preserving call sites in generic gpiolib lifecycle paths.

## State And Persistence
The header owns no runtime state. Its main persistence behavior is ABI-like internal contract stability between the ACPI implementation and generic gpiolib callers.

## Dependencies And Integration Points
It depends on `linux/err.h`, `linux/types.h`, and `linux/gpio/consumer.h`, with forward declarations for `gpio_chip`, `gpio_desc`, `gpio_device`, `device`, and `fwnode_handle`. It is integrated by `gpiolib-acpi-core.c`, `gpiolib-acpi-quirks.c`, and generic gpiochip registration paths.

## Risks
Stub return values affect generic fallback behavior in non-ACPI builds; changing them can alter probe deferral or not-found semantics. Any signature change requires coordinated updates across gpiolib and ACPI helpers.

## Test Signals
Build-test both `CONFIG_ACPI=y` and `CONFIG_ACPI=n`, verify non-ACPI builds link with stubs, and run ACPI GPIO lookup and gpiochip lifecycle tests in ACPI-enabled builds.
