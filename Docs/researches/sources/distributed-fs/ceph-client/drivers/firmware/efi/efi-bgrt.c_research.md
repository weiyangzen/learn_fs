# sources/distributed-fs/ceph-client/drivers/firmware/efi/efi-bgrt.c

Purpose: validates the ACPI Boot Graphics Resource Table image pointer, records the BGRT metadata, and reserves the firmware boot-logo BMP so later ACPI/sysfs BGRT consumers can expose it safely.

Important APIs/types/functions: global outputs are `struct acpi_table_bgrt bgrt_tab` and `size_t bgrt_image_size`. Main function is `efi_bgrt_init()`, with private `struct bmp_header`.

Control flow: `efi_bgrt_init()` exits if ACPI is disabled or EFI memory information is unavailable. It validates table length, accepts version 0 or 1 for compatibility, requires BMP image type 0 and a nonzero image address, checks the image address EFI memory type, maps the BMP header, checks magic `BM`, records image size, and reserves the image with `efi_mem_reserve()`. Any validation failure zeroes `bgrt_tab`.

State and persistence behavior: retained globals hold the validated BGRT table and image size. The image memory is reserved from general allocation.

Dependencies and integration points: called from ACPI/EFI BGRT discovery paths and depends on EFI memory type lookup, early memremap, ACPI table structures, and EFI memory reservation.

Risks and test signals: firmware may report invalid addresses, bad image types, or wrong memory types. Test signals include BGRT sysfs consumers seeing a nonzero image, logs for ignored invalid BGRT tables, and reserved boot-logo memory not being reused.
