# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_util.c

Purpose: shared WMI method helper layer for TUXEDO NB04 drivers. It hides ACPI buffer setup, WMI method evaluation, output type validation, and fixed-size buffer copying.

Important APIs and control flow: `__wmi_method_acpi_object_out()` builds input/output `acpi_buffer` structures, calls `wmidev_evaluate_method()`, and returns an allocated ACPI object. `__wmi_method_buffer_out()` wraps it, requires `ACPI_TYPE_BUFFER`, checks the returned length is at least the expected size, and copies bytes to the caller's union. Public wrappers `tux_wmi_xx_8in_80out()` and `tux_wmi_xx_496in_80out()` bind method IDs to the NB04 ABI sizes.

State and dependencies: no persistent state. It depends on the WMI core, ACPI object lifetimes, `__free(kfree)` cleanup, and the packed ABI unions declared in `wmi_util.h`.

Risks and test signals: wrong buffer sizes corrupt firmware calls or truncate outputs; non-buffer ACPI returns and short buffers must fail. Debug hex dumps may expose raw firmware inputs when dynamic debug is enabled. Tests should mock or exercise WMI methods for success, ACPI failure, null output, wrong object type, short output, and exact/oversized buffers.
