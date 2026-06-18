# sources/distributed-fs/ceph-client/drivers/firmware/efi/capsule-loader.c

Purpose: implements `/dev/efi_capsule_loader`, a misc character device that accepts an EFI capsule image from userspace and submits it to firmware through the EFI capsule core.

Important APIs/types/functions: key routines are `efi_capsule_open()`, `efi_capsule_write()`, `efi_capsule_release()`, `efi_capsule_submit_update()`, weak `efi_capsule_setup_info()`, shared `__efi_capsule_setup_info()`, and `efi_free_all_buff_pages()`. It uses `struct capsule_info` from EFI headers.

Control flow: each open allocates a fresh capsule state with arrays for pages and physical addresses. Writes must be sequential; data is copied page by page from userspace. Once enough bytes are available for the header, `efi_capsule_setup_info()` copies header fields, validates firmware support via `efi_capsule_supported()`, determines total size, and resizes page/phys arrays. When `count >= total_size`, the pages are optionally `vmap()`ed and submitted through `efi_capsule_update()`. Errors free buffered pages and set `NO_FURTHER_WRITE_ACTION` so later writes fail until close.

State and persistence behavior: incomplete uploads own allocated pages until close or error. Successfully submitted pages are intentionally not freed because persistent capsules may need to survive until reboot. Device registration persists while the module is loaded.

Dependencies and integration points: depends on EFI runtime services, capsule support in `capsule.c`, miscdevice, highmem mapping, user-copy APIs, and platform-specific weak overrides such as Quark capsule quirks.

Risks and test signals: accepting firmware-update data is sensitive; oversized writes, invalid headers, unsupported flags, allocation failure, and incomplete close paths must fail cleanly. Test signals include device node creation only with EFI runtime services, successful capsule upload logs, `-EIO` after failed writes until close, and firmware reset-type reporting for persistent capsules.
