## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/kaslr.c

### Purpose
`compressed/kaslr.c` implements early physical and virtual kernel address randomization. It gathers entropy, parses memory restrictions, builds avoid ranges, scans EFI/E820/KHO memory maps, and chooses a safe aligned load address for decompression.

### Important APIs, Types, And Functions
The exported function is `choose_random_location()`. Important helpers include `get_boot_seed()`, `parse_memmap()`, `mem_avoid_memmap()`, `parse_gb_huge_pages()`, `handle_mem_options()`, `mem_avoid_init()`, `mem_avoid_overlap()`, `store_slot_info()`, `process_gb_huge_pages()`, `slots_fetch_random()`, `__process_mem_region()`, `process_mem_region()`, `process_efi_entries()`, `process_e820_entries()`, `process_kho_entries()`, `find_random_phys_addr()`, and `find_random_virt_addr()`. State includes `mem_limit`, `memmap_too_large`, `mem_avoid`, `num_immovable_mem`, `slot_areas`, `slot_area_index`, `slot_max`, and `max_gb_huge_pages`.

### Control Flow
`choose_random_location()` exits early for `nokaslr`, sets `KASLR_FLAG`, initializes the memory limit, records avoid ranges for the compressed image, initrd, command line, boot params, setup_data, command-line `mem`/`memmap`, and ACPI immovable regions, then scans KHO scratch areas, EFI memory, or E820 RAM. Candidate regions are aligned, clipped by avoid overlaps, filtered for huge-page reservations and immovable memory when applicable, converted into slot counts, and one slot is chosen by `kaslr_get_random_long()`. On x86_64 it also chooses a randomized virtual address within `KERNEL_IMAGE_SIZE`.

### State, Persistence, And Dependencies
State persists only during the decompression decision plus `KASLR_FLAG` in boot params and updated output/virtual address values. Dependencies include shared KASLR entropy code, command-line parsing, ACPI immovable-memory detection, EFI memory descriptors, E820 table entries, setup_data, initrd boot fields, and decompressor image layout constants.

### Integration Points
`misc.c` calls `choose_random_location()` before accepting memory and decompressing. The chosen output and virtual address drive ELF relocation and final kernel entry behavior. ACPI, EFI, and KHO support feed candidate/avoid ranges.

### Risks
Incorrect avoid ranges can overwrite the compressed image, initrd, command line, setup_data, or preserved kexec handover memory. More than four unusable `memmap=` regions disables physical KASLR. EFI memory handling is conservative because some firmware expects boot-services memory untouched until later runtime transitions.

### Test Signals
Boot with `nokaslr`, multiple `mem=` and `memmap=` forms, initrd, command line near the kernel, setup_data chains including indirect entries, EFI memory maps with mirrored and soft-reserved memory, E820-only boots, KHO handover, 1 GiB huge page reservations, and memory hotremove SRAT filtering.
