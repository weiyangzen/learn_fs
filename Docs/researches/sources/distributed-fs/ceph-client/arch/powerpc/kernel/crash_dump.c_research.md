<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c

## Purpose
`crash_dump.c` implements PowerPC kdump support helpers. It reserves low memory for kdump trampolines, creates branch trampolines for non-static kernels, copies memory from the crashed kernel image, distinguishes kdump from firmware-assisted dump, and frees crashkernel pages while preserving RTAS memory.

## Important APIs, Types, And Functions
Key functions are `reserve_kdump_trampoline()`, `setup_kdump_trampoline()`, private `create_trampoline()`, `copy_oldmem_page()`, exported `is_kdump_kernel()`, and RTAS-specific `crash_free_reserved_phys_range()`. It uses `patch_instruction()`, `patch_branch()`, memblock APIs, `ioremap_cache()`, `copy_to_iter()`, `is_fadump_active()`, and RTAS device-tree properties.

## Control Flow
On non-static kernels, low memory is reserved and trampoline slots are populated every eight bytes. `create_trampoline()` emits a NOP followed by a branch that effectively reaches `addr + PHYSICAL_START`. `copy_oldmem_page()` uses direct mapping for normal memory and temporary cached ioremap for non-memory regions. `is_kdump_kernel()` returns true only for kexec crash dumps, not fadump. RTAS page freeing skips pages overlapping the RTAS reserved region.

## State And Persistence
State effects are boot-time memblock reservations, patched trampoline instructions in low memory, and page reservation accounting. There is no file-backed persistence.

## Dependencies And Integration Points
It integrates with kexec/kdump, `/proc/vmcore` oldmem reads, pSeries FWNMI trampoline addresses, fadump, RTAS, and crashkernel memory management.

## Risks
Branch range assumptions are delicate and tied to the trampoline layout. `copy_oldmem_page()` must avoid invalid direct mappings for non-RAM. Freeing crashkernel pages without RTAS overlap checks can corrupt firmware runtime services.

## Test Signals
Signals include successful kdump boot and vmcore reads, reserved low memory visibility, correct FWNMI trampoline behavior on pSeries, `is_kdump_kernel()` false under fadump, and no RTAS failures after shrinking crashkernel memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/crash_dump.c -->
