# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_util.c

## Purpose
Provides a shared ELF PT_LOAD firmware loader used by non-META firmware processor backends.

## Important APIs, types, and functions
- `pvr_fw_process_elf_command_stream()` walks an ELF32 program header table and copies loadable segments into the appropriate firmware section allocations.

## Control flow
The function treats the firmware buffer as an ELF32 image, obtains the program header table from `e_phoff`, iterates `e_phnum` entries, skips non-`PT_LOAD` entries, resolves each loadable virtual address and memory size through `pvr_fw_find_mmu_segment()`, copies `p_filesz` bytes from the firmware file, and zeroes the remaining `p_memsz - p_filesz` bytes.

## State and persistence
It does not own state. It mutates the host-side code/data/core memory images passed by the caller; those images are later copied into FW objects and retained as reset shadows by `pvr_fw.c`.

## Dependencies and integration points
Depends on Linux ELF definitions, common firmware segment lookup, and DRM error logging. Used by MIPS and RISC-V firmware processing, while META uses its LDR parser.

## Risks
This is firmware input parsing. It relies on the firmware validator and `pvr_fw_find_mmu_segment()` for bounds/section checks, but it does not independently validate ELF header bounds, program header bounds, or `p_offset + p_filesz` against the firmware size. Malformed ELF metadata could therefore drive out-of-bounds reads if accepted earlier.

## Test signals
Use valid MIPS/RISC-V ELF firmware, PT_LOAD sections spanning code/data/core ranges, zero-fill behavior where `p_memsz > p_filesz`, invalid virtual addresses, and malformed ELF headers/program tables to validate rejection or hardening.
