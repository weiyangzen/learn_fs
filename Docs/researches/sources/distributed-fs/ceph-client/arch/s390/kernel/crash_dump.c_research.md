# sources/distributed-fs/ceph-client/arch/s390/kernel/crash_dump.c

## Purpose
Implements s390 crash dump support for kdump and zfcp/nvme dump environments. It copies old memory, remaps `/proc/vmcore`, builds ELF core headers, and records CPU register save areas.

## Important APIs, Types, And Functions
Save-area APIs are `save_area_alloc()`, `save_area_boot_cpu()`, `save_area_add_regs()`, and `save_area_add_vxrs()`. Old-memory APIs include `copy_oldmem_page()`, `copy_oldmem_kernel()`, and `remap_oldmem_pfn_range()`. ELF header APIs include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, and optional `elfcorehdr_fill_device_ram_ptload_elf64()`.

## Control Flow
During crash kernel setup, CPU lowcore register state is copied into linked save areas. Old memory reads choose HSA copying for dump IPL or real-memory copying with kdump address swapping. `elfcorehdr_alloc()` validates dump mode, initializes oldmem ranges, counts memory/text headers, allocates an ELF buffer, emits `PT_NOTE` notes for process info, CPU regs, timers, control regs, prefix, vector regs, and vmcoreinfo, then emits `PT_LOAD` program headers for memory and optional old kernel text.

## State And Persistence
State includes `oldmem_region`, `oldmem_type`, `dump_save_areas`, and the allocated ELF header passed to vmcore. It represents previous-kernel memory and CPU state until freed.

## Dependencies And Integration Points
Depends on crash dump core, memblock, ELF, SCLP HSA access, old OS info, IPL type detection, lowcore layout, vector/FPU support, and `/proc/vmcore`.

## Risks And Edge Cases
Address swapping for crashkernel memory is subtle. zfcp/nvme HSA below `sclp.hsa_size` cannot be remapped and must be copied. ELF note sizing must match emitted data. Missing header allocation panics intentionally to allow alternate dump mechanisms.

## Test Signals
Signals include kdump boot, zfcp/nvme dump IPL, `/proc/vmcore` read and mmap tests, crash utility parsing, vector-register note presence when VX is available, and memory range correctness with KASLR old OS info.
