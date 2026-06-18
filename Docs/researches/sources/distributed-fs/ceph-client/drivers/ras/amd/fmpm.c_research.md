# sources/distributed-fs/ceph-client/drivers/ras/amd/fmpm.c

Purpose: implements AMD FRU Memory Poison Manager. It records MI300 memory poison descriptors in CPER records stored through ACPI ERST, replays saved poison records at boot, retires affected DRAM rows, and exposes a debugfs view of FRU entries and translated system physical addresses.

Important APIs and types: core structures are `cper_sec_fru_mem_poison`, `cper_fru_poison_desc`, and packed `fru_rec`. Module entry and exit are `fru_mem_poison_init()` and `fru_mem_poison_exit()`. Key functions include `update_record_on_storage()`, `get_saved_records()`, `save_new_records()`, `update_fru_record()`, `fru_handle_mem_poison()`, `retire_mem_records()`, `save_spa()`, `fmpm_show()`, and `setup_debugfs()`. The module parameter `max_nr_entries` sizes each FRU record.

Control flow: init gates on AMD family 0x19, MI300A model range, PPIN support, ERST availability, and package count. It allocates one record per FRU/socket, initializes FRU metadata from CPU CPUID and PPIN, loads matching persistent records, writes new or grown records, creates `ras/fmpm/entries`, retires saved rows, and registers an MCE notifier. On memory-error notification, it retires the row, finds a FRU by PPIN, filters duplicates, appends a descriptor if capacity allows, translates and caches SPA, recalculates checksum, and writes the CPER record to ERST.

State and persistence: `fru_records` and `spa_entries` are runtime caches; ERST CPER records are persistent. `fmpm_update_mutex` serializes record updates and debugfs reads. Saved records with invalid checksum or absent FRU are cleared.

Dependencies and integration: uses x86 MCE notifier chain, CPER helpers, ERST, AMD topology/PPIN, ATL row retirement and address conversion, and RAS debugfs root.

Risks: ERST write failure fails init for new records or loses updates later. Fixed MI300 assumptions limit portability. `max_nr_entries` bounds descriptors; overflow only warns. Persistent records larger than current configuration force `-EINVAL`. Boot-time retirement occurs after dependencies initialize, leaving an early exposure window.

Test signals: ERST unavailable, invalid CPER checksum clearing, record growth, duplicate descriptor filtering with masked column/row13 bits, capacity overflow, debugfs formatting, notifier handling of non-memory errors, saved-record replay, and cleanup on failed init.
