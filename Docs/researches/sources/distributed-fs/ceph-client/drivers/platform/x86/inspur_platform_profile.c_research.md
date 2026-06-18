<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c

## Purpose
Implements Inspur WMI integration with the generic Linux platform profile API. It exposes EC power modes as `low-power`, `balanced`, and `performance` platform profiles through a WMI GUID.

## Important APIs, Types, And Functions
The driver matches `WMI_INSPUR_POWERMODE_BIOS_GUID`. `inspur_wmi_perform_query()` wraps `wmidev_evaluate_method()` and validates ACPI buffer replies. `inspur_platform_profile_get()` and `inspur_platform_profile_set()` translate between `enum platform_profile_option` and Inspur EC mode bytes. `inspur_platform_profile_probe()` declares supported choices.

## Control Flow
WMI probe allocates `struct inspur_wmi_priv`, stores the WMI device, then calls `devm_platform_profile_register()`. Reads issue method `0x02`, check return code byte 0, and decode mode byte 1. Writes place the desired mode in byte 0, issue method `0x03`, then treat a nonzero returned byte 0 as EC failure.

## State And Persistence
Driver state is just the device-private WMI pointer and platform-profile device. Persistent state lives in EC RAM/firmware power-mode settings, not in this module.

## Dependencies And Integration Points
Depends on ACPI WMI and `platform_profile`. It integrates with userspace through `/sys/firmware/acpi/platform_profile` style platform profile interfaces managed by the core.

## Risks And Test Signals
Risks are firmware ABI mismatch, unexpected ACPI object type or length, and unsupported EC mode values. Test by loading on matching Inspur hardware, reading/writing all three profile choices, checking error handling for invalid values, and verifying WMI method failures are surfaced as negative errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c -->
