# sources/distributed-fs/ceph-client/drivers/of/kexec.c

## Purpose
`kexec.c` prepares a new FDT for a kexec or crash-kernel boot. It removes stale reservations and properties, carries forward or replaces initrd and bootargs, adds crash dump metadata, random seeds, IMA buffers, and kexec handover metadata.

## Important APIs, types, and functions
The main exported-style API is `of_kexec_alloc_and_setup_fdt()`. Helpers include `fdt_find_and_del_mem_rsv()`, `get_addr_size_cells()`, `do_get_kexec_buffer()`, `ima_get_kexec_buffer()`, `ima_free_kexec_buffer()`, `remove_ima_buffer()`, `setup_ima_buffer()`, and `kho_add_chosen()`.

## Control flow and state
`of_kexec_alloc_and_setup_fdt()` sizes a new buffer from current `initial_boot_params`, command line length, fixed extra space, and caller extra space. It opens the current FDT into the new buffer, removes the current FDT reservation, ensures `/chosen` exists, removes stale crash properties, replaces initrd properties and reservation, adds crash elfcorehdr and usable-memory-range for crash images, adds KHO metadata, updates bootargs, refreshes `kaslr-seed` and `rng-seed` only if the RNG is initialized, marks `linux,booted-from-kexec`, removes old IMA buffer metadata, and optionally adds a new IMA buffer reservation.

IMA helper functions parse `linux,ima-kexec-buffer` using root address/size cells and validate or free the region via memblock.

## Dependencies and integration
This file depends on libfdt mutation APIs, kexec image fields, memblock, IMA, random subsystem, crash dump resources, dm-crypt crash-key handoff, root cell-count helpers from OF core, and `initial_boot_params`.

## Risks and test signals
Risks include insufficient FDT slack, failed reservation deletion, stale sensitive seeds, malformed address/size properties, missing `/chosen`, RNG unavailability, and losing crash metadata. Test signals are successful kexec/kdump boot, FDT property inspection in the next kernel, reservation map correctness, and IMA measurement carryover.
