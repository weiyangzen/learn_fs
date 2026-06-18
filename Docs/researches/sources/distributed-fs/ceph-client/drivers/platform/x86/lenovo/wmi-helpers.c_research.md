<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c

## Purpose
This file provides shared Lenovo Legion WMI helper functionality: a common method evaluator for integer-returning WMI methods and a blocking notifier chain for querying the current GameZone thermal mode.

## Important APIs, Types, And Functions
`lwmi_dev_evaluate_int()` wraps `wmidev_evaluate_method()`, passes arbitrary input buffers, and accepts either ACPI integer returns or little-endian u32 values in ACPI buffers. `lwmi_tm_register_notifier()`, `lwmi_tm_unregister_notifier()`, and `devm_lwmi_tm_register_notifier()` manage the thermal-mode notifier chain. `lwmi_tm_notifier_call()` asks subscribers for the current thermal mode using action `LWMI_GZ_GET_THERMAL_MODE`.

## Control Flow
The WMI helper builds input and output ACPI buffers, calls the WMI method, validates output only if a return pointer is requested, and converts accepted object types into a u32 result. The notifier helper registers a consumer-owned `notifier_block`; `lwmi_tm_notifier_call()` calls the chain and returns `-EINVAL` unless the non-stop status is `NOTIFY_OK`.

## State And Persistence
The only persistent state is the global blocking notifier chain. No WMI state is cached here.

## Dependencies And Integration Points
The file depends on ACPI/WMI, notifier chains, cleanup helpers, unaligned little-endian reads, and `wmi-helpers.h`. `wmi-gamezone.c` registers the thermal-mode responder; `wmi-other.c` uses `lwmi_tm_notifier_call()` before reading or writing mode-dependent attributes; several Lenovo WMI drivers use `lwmi_dev_evaluate_int()`.

## Risks And Edge Cases
Firmware may return buffers instead of integers; this file intentionally handles that Windows-compatible behavior. Short buffers and unsupported object types return `-ENXIO`. `lwmi_tm_notifier_call()` passes `&mode` to the notifier chain, so responders expect an `enum thermal_mode **`; mismatched consumers would corrupt results.

## Test Signals
Tests should cover integer returns, buffer returns, null or short outputs, WMI call failures, notifier registration/unregistration, and `lwmi_tm_notifier_call()` behavior when no provider is registered or a provider returns a non-OK status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c -->
