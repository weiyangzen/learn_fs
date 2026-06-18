
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-flash.c

Purpose: implements the sysfs firmware update interface for OPAL-managed PowerNV firmware images.

Important APIs/types/functions: global structures track candidate `image_data`, `validate_flash_data`, `manage_flash_data`, and `update_flash_data`. Sysfs files are `image` (binary write), `validate_flash`, `manage_flash`, and `update_flash`. Important functions include `image_data_write()`, `alloc_image_buf()`, `free_image_buf()`, `opal_flash_validate()`, `opal_flash_manage()`, `opal_flash_update()`, `opal_flash_update_print_message()`, and `opal_flash_update_init()`.

Control flow: init checks `OPAL_FLASH_VALIDATE`, allocates a 4 KiB validation buffer, creates sysfs files under `/sys/firmware/opal`, and initializes statuses. Userspace writes the firmware image to `image`; the first write parses the header for total size, allocates a vmalloc buffer, pins pages with `SetPageReserved`, and subsequent writes fill the buffer until ready. `validate_flash` copies the first 4 KiB and invokes OPAL validation. `manage_flash` commits or rejects temporary firmware sides. `update_flash` initiates or cancels update; initiating builds an OPAL SG list and calls `opal_update_flash()`. Reboot path prints warning messages when an update is pending.

State and persistence: candidate image and status values persist in kernel memory until replaced, freed, or rebooted. Firmware update state persists in OPAL once initiated. Mutex `image_data_mutex` serializes image operations.

Dependencies and integration points: depends on OPAL flash calls, sysfs/kobject infrastructure, vmalloc SG helpers, reboot messaging, and userspace firmware update tooling.

Risks: privileged sysfs writes can stage firmware updates. Image size is trusted from header after bounds checks and capped at 1 GiB. Page reservation and SG-list handling must match OPAL expectations. Status fields are reset on some reads, making userspace ordering observable.

Test signals: sysfs file creation, invalid/short/oversized image rejection, chunked image writes, validation status/result text, update cancel/init paths, manage commit/reject, reboot warning output, and memory cleanup on replacement.
