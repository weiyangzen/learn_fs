
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/primary_display.c

Purpose: allocates and publishes EFI primary display information for sysfb consumers when direct access to the kernel global is unavailable, especially zboot.

Important APIs/types/functions: exports `__alloc_primary_display()` and `free_primary_display()`.

Control flow: allocation reserves an `EFI_ACPI_RECLAIM_MEMORY` pool object, zeroes it, installs it under `LINUX_EFI_PRIMARY_DISPLAY_TABLE_GUID`, and returns it. Freeing removes the configuration table and frees the pool allocation.

State and persistence behavior: the display-info object persists as an EFI configuration table until consumed by the kernel or explicitly freed after failed/common boot handoff.

Dependencies and integration points: depends on EFI boot services and Linux `sysfb_display_info`. It is called by common stub display setup and zboot's `alloc_primary_display()` wrapper.

Risks and test signals: failure to uninstall on error leaves stale table data. Test signals include zboot framebuffer earlycon availability, config-table presence/absence around allocation/free, and allocation failure handling.
