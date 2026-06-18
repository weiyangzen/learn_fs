<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c

## Purpose
This small MXM WMI helper exposes functions for GPU mux switching through the MXM WMMX WMI GUID.

## Important APIs, Types, And Functions
The target GUID is `F6CB5C3C-9CAE-4EBD-B577-931EA32A2CC0`. `struct mxds_args` carries function code, args, and xarg. Exported functions are `mxm_wmi_call_mxds()`, `mxm_wmi_call_mxmx()`, and `mxm_wmi_supported()`. Function codes are four-character constants for `MXDS` and `MXMX`.

## Control Flow
`mxm_wmi_supported()` checks GUID presence. The call helpers build the argument struct with selected function code and call `wmi_evaluate_method()` using the adapter value as method ID. They print before and after the call and return ACPI failure status directly or `0` on success.

## State And Persistence
The file maintains no state. Any mux state change is performed by firmware in response to WMI calls.

## Dependencies And Integration Points
It depends on WMI and exports symbols through GPL for graphics or platform code that needs MXM mux operations. It also relies on public `linux/mxm-wmi.h` declarations.

## Risks And Edge Cases
Return values on ACPI failure are raw `acpi_status`, not normalized Linux negative errno. The helpers use `printk()` instead of structured device logging and have no locking or result validation. Firmware behavior is opaque and adapter method IDs must match platform expectations.

## Test Signals
Tests should verify GUID detection, successful MXDS/MXMX calls on supported hardware, caller handling of raw ACPI failure values, and no calls on unsupported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c -->
