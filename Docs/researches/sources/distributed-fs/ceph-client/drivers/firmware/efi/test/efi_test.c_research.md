# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.c

Purpose: Exposes selected EFI runtime services to privileged userspace through a misc device named `efi_test`. It is a diagnostic/testing bridge for firmware operations such as variable access, time services, wake alarm, monotonic count, capsule capability query, reset, and runtime support mask reporting.

Important APIs/types/functions: Helpers copy UCS-2 strings between user and kernel memory. IOCTL handlers include `efi_runtime_get_variable()`, `efi_runtime_set_variable()`, `efi_runtime_get_time()`, `efi_runtime_set_time()`, `efi_runtime_get_waketime()`, `efi_runtime_set_waketime()`, `efi_runtime_get_nextvariablename()`, `efi_runtime_query_variableinfo()`, `efi_runtime_query_capsulecaps()`, and `efi_runtime_reset_system()`. `efi_test_ioctl()` dispatches the ioctl numbers from `efi_test.h`.

Control flow: `efi_test_init()` registers a misc device. `open` rejects use under EFI lockdown and requires `CAP_SYS_ADMIN`. Each ioctl copies a packed userspace request, marshals optional pointers and buffers, calls the matching `efi.*` runtime service, writes EFI status back to userspace, and returns Linux errors for copy or firmware failures.

State and persistence behavior: The driver itself is stateless aside from misc-device registration. It can mutate persistent EFI NVRAM through set-variable, system time/wake alarm through EFI services, and can trigger reset through `efi.reset_system()`.

Dependencies and integration points: Relies on the global EFI runtime-services table, Linux security lockdown, capability checks, miscdevice, uaccess, and the ABI structs in `efi_test.h`. It can test whichever EFI variable backend is active, including generic, GSMI, or TEE STMM.

Risks and test signals: This is intentionally powerful and must remain locked to admin and lockdown policy. User pointer validation, buffer-size reporting, and capsule pointer-array copying are high-risk paths. Test with negative uaccess cases, zero-length/oversized buffers, EFI_BUFFER_TOO_SMALL propagation, lockdown enforcement, and each ioctl against known EFI firmware or a virtualized EFI environment.
