# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_platform.c

## Purpose
`fallback_platform.c` loads firmware embedded in platform firmware, such as EFI embedded firmware, when the request opts into platform fallback.

## Important APIs, Types, And Functions
The single function is `firmware_fallback_platform(struct fw_priv *fw_priv)`. It uses `FW_OPT_FALLBACK_PLATFORM`, `efi_get_embedded_fw()`, `security_kernel_load_data()`, `security_kernel_post_load_data()`, `vmalloc()`, and `fw_state_done()`.

## Control Flow, State, And Persistence
The function first verifies the request option, asks LSMs whether firmware loading is allowed, looks up embedded data by firmware name, checks that it fits a preallocated buffer if present, runs post-load security validation, allocates a buffer when needed, copies the platform data, stores size, and marks the firmware request complete.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates with the main request flow after filesystem and compressed lookup fail but before sysfs fallback. Dependencies include EFI embedded firmware support, security hooks, and vmalloc. Risks include copying untrusted platform data without security approval, buffer-too-small handling, distinguishing `-ENOENT` from policy errors, and memory ownership by `fw_priv`. Test signals include opt-in versus no-opt behavior, embedded hit/miss, LSM denial, preallocated buffer size checks, and release freeing allocated copies.
