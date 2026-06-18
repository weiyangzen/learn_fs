# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.c

Purpose: HFI1 EFI variable reader. It retrieves per-device firmware/platform data stored as EFI runtime variables under an HFI1-specific GUID, using PCI domain/bus/slot/function plus a caller-provided kind suffix.

Important APIs/functions: internal `read_efi_var()` reads a named EFI variable into a kmalloc buffer and returns its actual size. Public `read_hfi1_efi_var()` builds `<domain>:<bus>:<slot>.<func>-<kind>`, tries lowercase PCI address first, then uppercase, and returns the allocated data to the caller.

Control flow: `read_efi_var()` checks EFI GetVariable support, allocates a UTF-16 variable name and 4 KiB temporary buffer, converts ASCII to UTF-16 by direct widening, calls `efi.get_variable()`, maps status to `0`, `-ENOENT`, or `-EINVAL`, duplicates the exact result length, and cleans temporary allocations. `read_hfi1_efi_var()` handles the name fallback.

State and persistence: no driver state persists here. Persistent data lives in firmware EFI variable storage. On success, ownership of a newly allocated buffer and size is transferred to the caller; on failure, outputs are guaranteed NULL/zero by `read_efi_var()`.

Dependencies and integration: depends on Linux EFI runtime support, PCI address helpers, `string_upper()`, and `struct hfi1_devdata` from `hfi.h`. It is an alternate platform configuration source alongside EPROM.

Risks: all non-success/non-not-found EFI statuses collapse to `-EINVAL`, losing diagnostics such as buffer-too-small. `EFI_DATA_SIZE` is fixed at 4096 bytes; larger variables are not retried with the required size. EFI runtime calls can be unavailable or platform-sensitive, so callers must handle `-EOPNOTSUPP`, `-ENOENT`, and malformed data.

Test signals: EFI unsupported path, missing variable path, lowercase and uppercase PCI-name fallback, correct buffer size/content return, allocation failure injection, and validation by the caller that consumes the returned platform data.
