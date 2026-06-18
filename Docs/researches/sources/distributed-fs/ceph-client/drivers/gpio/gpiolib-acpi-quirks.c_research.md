# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-acpi-quirks.c

## Purpose
`gpiolib-acpi-quirks.c` contains platform-specific policy for ACPI GPIO event handling. It controls whether edge-triggered ACPI event handlers run at boot, supports module-parameter override lists for ignoring wake or interrupt handling on specific controller/pin pairs, defers early ACPI IRQ registration until late init, and applies DMI-based defaults for machines with broken firmware behavior.

## Important APIs, Types, And Functions
The externally used helpers are `acpi_gpio_add_to_deferred_list()`, `acpi_gpio_remove_from_deferred_list()`, `acpi_gpio_need_run_edge_events_on_boot()`, and `acpi_gpio_in_ignore_list()`. `struct acpi_gpiolib_dmi_quirk` stores the DMI-derived actions: suppress boot edge events, ignore wake, and ignore interrupts. `gpiolib_acpi_quirks[]` is the DMI match table.

## Control Flow
At `postcore_initcall`, `acpi_gpio_setup_params()` finds the first matching DMI quirk and fills unset module parameters. If `run_edge_events_on_boot` remains automatic, it becomes disabled for affected machines and enabled otherwise. `ignore_wake` and `ignore_interrupt` are set from DMI only when the user did not provide module parameters.

GPIO chips that call ACPI interrupt registration too early enter `acpi_gpio_deferred_req_irqs_list` through `acpi_gpio_add_to_deferred_list()`. At `late_initcall_sync`, `acpi_gpio_handle_deferred_request_irqs()` processes the list by calling `acpi_gpio_process_deferred_list()` and then flips `acpi_gpio_deferred_req_irqs_done`, causing later chips to request IRQs immediately.

`acpi_gpio_in_ignore_list()` parses comma-separated `controller@pin` strings and compares controller names and numeric pins against the queried GPIO. Malformed input logs one error and returns false.

## State And Persistence
Global state consists of module parameters, a mutex-protected deferred IRQ list, and a boolean indicating that deferred processing has completed. The settings persist for the boot lifetime. DMI quirk data is `__initconst`; selected strings are installed into global pointers during init.

## Dependencies And Integration Points
The file depends on DMI matching, module parameter handling, list/mutex primitives, and the ACPI GPIO header. It is consumed directly by `gpiolib-acpi-core.c` when deciding whether to request ACPI event IRQs now, whether to synthesize boot edge events, and whether to ignore firmware wake or interrupt declarations.

## Risks
String parsing is intentionally simple and strict; a malformed user parameter disables all matches in that list after logging. DMI quirks are hardware-specific and can become stale as firmware changes. Deferral ordering is sensitive because it exists to let other built-in drivers register OpRegions before ACPI event methods can run.

## Test Signals
Test with module parameters overriding DMI defaults, DMI-matched machines that disable boot edge events, ignore-wake and ignore-interrupt lists with valid and invalid syntax, early gpiochip registration before late init, and late gpiochip registration after the deferred list has been drained.
