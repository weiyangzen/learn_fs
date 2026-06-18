# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_loader.c

## Purpose
Implements the default ELF32/ELF64 firmware loader for remoteproc. It validates firmware, extracts boot addresses, loads `PT_LOAD` segments, caches `.resource_table`, and locates the loaded resource table in remote memory.

## Important APIs, Types, And Functions
Exports `rproc_elf_sanity_check()`, `rproc_elf_get_boot_addr()`, `rproc_elf_load_segments()`, `rproc_elf_load_rsc_table()`, and `rproc_elf_find_loaded_rsc_table()`. Internal `find_table()` scans section headers for `.resource_table` and validates the remoteproc table header.

## Control Flow
Sanity checking verifies firmware presence, minimum header size, ELF magic, class, host-matching endianness, section-header availability, nonzero program-header count, and program-header offset. Segment loading iterates program headers, skips non-loadable or empty entries, rejects `filesz > memsz`, truncated payloads, and unrepresentable sizes, translates device address through `rproc_da_to_va()`, copies data, and zeroes BSS with normal or I/O memory helpers.

Resource-table loading finds `.resource_table`, validates version, reserved fields, and offset array size, copies it to `rproc->cached_table`, and sets `table_ptr`/`table_sz`. After firmware is loaded, `rproc_elf_find_loaded_rsc_table()` translates the section address and size to a live kernel mapping.

## State And Persistence Behavior
The loader writes firmware bytes into memory prepared by core/platform carveouts. It allocates and owns `rproc->cached_table` until core cleanup. The cached table is later mutated by resource handling and virtio setup, then copied back into loaded remote memory.

## Dependencies And Integration Points
Used as default by `rproc_alloc_ops()` when platform drivers do not override load/parse/sanity/boot-address callbacks. Depends on `remoteproc_elf_helpers.h`, `rproc_da_to_va()`, and the remoteproc resource-table ABI.

## Risks
Firmware endianness must match the host. `find_table()` is not a full ELF verifier and relies on preceding sanity checks. Missing resource tables cause this parser to fail unless a platform wrapper intentionally tolerates the absence. Platform memory maps must be registered before segment load or address translation fails.

## Test Signals
Use valid ELF32/ELF64 images plus bad magic, wrong endian, missing program headers, truncated section/resource tables, `filesz > memsz`, out-of-range offsets, oversized `memsz`, missing resource table, and segment addresses outside carveouts. Confirm BSS zeroing and resource-table copy-back after vring assignment.
