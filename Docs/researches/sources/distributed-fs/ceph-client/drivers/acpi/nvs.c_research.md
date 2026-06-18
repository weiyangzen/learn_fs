# sources/distributed-fs/ceph-client/drivers/acpi/nvs.c

`nvs.c` records ACPI NVS regions and, with ACPI sleep enabled, saves and restores their contents across suspend/resume.

Important APIs are `acpi_nvs_register()`, `acpi_nvs_for_each_region()`, and under `CONFIG_ACPI_SLEEP`, `suspend_nvs_alloc()`, `suspend_nvs_save()`, `suspend_nvs_restore()`, and `suspend_nvs_free()`. `struct nvs_region` stores boot-lifetime region metadata; `struct nvs_page` stores page-bounded suspend backup entries, saved data, mapped address, and unmap mode.

Registration appends raw regions and splits them into page-bounded save entries. Suspend allocation reserves backup pages, save maps each physical fragment using an existing ACPI mapping or fallback ioremap and copies data out, restore copies data back with interrupts disabled, and free releases backup pages and mappings later.

Dependencies include ACPI OSL mapping helpers, kernel list/slab/page APIs, ACPI sleep, and APEI iteration. Risks include partial registration on allocation failure, many backup pages for fragmented NVS, losing restore data after save failure cleanup, and restore depending on mappings established during save. Test signals include aligned/unaligned regions, allocation failure, existing mapping vs fallback ioremap, byte-accurate save/restore, no-sleep stubs, and region iterator early exit.
