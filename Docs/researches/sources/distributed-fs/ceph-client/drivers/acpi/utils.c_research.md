# sources/distributed-fs/ceph-client/drivers/acpi/utils.c

## Purpose

`utils.c` is a collection of ACPI core helper APIs for evaluating common AML objects, extracting ACPI packages, managing ACPI handle lists, formatting ACPI handle logs, checking device presence and matches, evaluating hotplug/control methods, handling `_DSM`, parsing boot parameters, and matching platform OEM table descriptors.

## Important APIs, types, and functions

Major exported helpers include `acpi_extract_package()`, `acpi_evaluate_integer()`, `_ADR` readers, `acpi_get_subsystem_id()`, `acpi_evaluate_reference()`, ACPI handle-list equal/replace/free helpers, `acpi_device_dep()`, `acpi_get_physical_device_location()`, `acpi_evaluate_ost()`, `acpi_handle_printk()`, dynamic-debug handle logging, `acpi_evaluation_failure_warn()`, `acpi_has_method()`, `acpi_execute_simple_method()`, `_EJ0`/`_LCK`/`_REG` evaluators, `_DSM` evaluation/check helpers, UID conversion, ACPI device found/present/match iterators, `acpi_reduced_hardware()`, `acpi_video_backlight_string`, and `acpi_match_platform_list()`.

## Control flow

Package extraction validates the requested format string, computes packed head/tail output storage, allocates or validates the caller buffer, and copies integers, strings, buffers, or references. Evaluation helpers wrap `acpi_evaluate_object()` with type checks and standardized logging. Reference-list helpers evaluate package references and manage allocated handle arrays. Hotplug helpers build method arguments for `_OST`, `_EJ0`, `_LCK`, and `_REG`. `_DSM` helpers evaluate function 0 to check support bitmasks or evaluate requested functions. Device-presence helpers search the ACPI bus by HID/UID/HRV after scan initialization. Platform matching reads table headers and compares OEM fields and revision predicates.

## State and persistence

Most helpers are stateless. `acpi_video_backlight_string` stores the `acpi_backlight=` boot parameter. Some helpers allocate caller-owned memory, including extracted package buffers, subsystem ID strings, PLD structures, `_DSM` objects, and ACPI handle-list arrays. Device match iterators transfer references that callers must release with `acpi_dev_put()`.

## Dependencies and integration points

The file is used broadly across ACPI scan, hotplug, thermal, video/backlight, platform quirks, device drivers, and logging code. It depends on ACPICA object evaluation/name/table APIs, Linux ACPI bus state from `scan.c`, dynamic debug, and `sleep.h` for reduced-hardware/sleep-related declarations.

## Risks

Memory ownership and type validation are the main risks: callers must free allocated buffers and handle `ERR_PTR`/NULL/`AE_*` returns correctly. `acpi_extract_package()` does not support nested packages. Logging with ACPI paths cannot run path lookup in interrupt context. Device-presence helpers require ACPI scan to have completed and only describe a point-in-time state for hotpluggable devices. `_DSM` support bit interpretation must preserve compatibility with integer and buffer returns.

## Test signals

Test malformed and valid ACPI packages, integer/reference evaluation, handle-list replacement/free paths, hotplug `_OST`/`_EJ0`/`_LCK` calls, `_DSM` integer and buffer support masks, device match helpers with HID/UID/HRV combinations, PLD decoding, `acpi_backlight=` storage, platform OEM matching, and dynamic-debug handle logging.
