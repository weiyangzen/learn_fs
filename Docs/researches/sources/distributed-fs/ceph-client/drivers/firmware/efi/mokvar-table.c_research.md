
# sources/distributed-fs/ceph-client/drivers/firmware/efi/mokvar-table.c

Purpose: validates a Linux EFI Machine Owner Key variable configuration table, reserves it, maps it for runtime kernel use, provides table iteration/search helpers, and exposes entries under `/sys/firmware/efi/mok-variables/`.

Important APIs/types/functions: exports `efi_mokvar_table_init()`, `efi_mokvar_entry_next()`, and `efi_mokvar_entry_find()`. Internal sysfs path uses `efi_mokvar_sysfs_read()` and `efi_mokvar_sysfs_init()`, with `struct efi_mokvar_sysfs_attr` list nodes.

Control flow: early init requires an EFI memmap and valid table physical address, verifies the table lies within one EFI memory descriptor, walks variable-size entries until a sentinel with empty name and zero data size, enforces name NUL termination, remaps headers as needed across pages, reserves boot-services memory, and records total size. Fs init memremaps the whole table, creates the `mok-variables` kobject, creates one read-only binary sysfs attribute per entry, and stores attributes in a permanent list. Reads require `CAP_SYS_ADMIN` and copy bounded entry data.

State and persistence behavior: `efi_mokvar_table_size`, `efi_mokvar_table_va`, `efi_mokvar_sysfs_list`, and `mokvar_kobj` persist after init. The table memory is reserved and mapped read-only to users via sysfs.

Dependencies and integration points: depends on EFI MOK config table discovery, EFI memory map lookup/reservation, early and late memremap, sysfs/kobject APIs, capabilities, and certificate-loading code that can query entries.

Risks and test signals: there is no table header, so validation must avoid walking outside one descriptor. Sysfs init error paths can leave mappings/kobjects partially present. Test signals include valid sentinel tables, malformed data sizes, tables crossing descriptors, boot-services reservation, entry find/iteration, CAP_SYS_ADMIN reads, and absence of table.
