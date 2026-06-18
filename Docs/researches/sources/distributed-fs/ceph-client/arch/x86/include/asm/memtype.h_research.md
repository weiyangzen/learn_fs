# sources/distributed-fs/ceph-client/arch/x86/include/asm/memtype.h

## Purpose
Declares x86 PAT and memory-type reservation APIs used to coordinate cacheability attributes for RAM, IO mappings, and kernel mappings.

## Important APIs, Types, And Functions
Functions include `pat_enabled()`, `pat_bp_init()`, `pat_cpu_init()`, `memtype_reserve()`, `memtype_free()`, `memtype_kernel_map_sync()`, `memtype_reserve_io()`, `memtype_free_io()`, `pat_pfn_immune_to_uc_mtrr()`, `x86_has_pat_wp()`, and `pgprot2cachemode()`.

## Control Flow
Callers reserve a physical range with a requested page cache mode and receive the effective mode. Kernel and IO mapping paths synchronize attributes with PAT/MTRR state. Free calls release reservations.

## State And Persistence
The header declares access to global PAT/memtype reservation state maintained elsewhere. Reservations persist while mappings or drivers hold them.

## Dependencies And Integration Points
Depends on Linux types, resources, and x86 page table cache-mode definitions. It integrates with ioremap, DRM/framebuffer WC mappings, MTRR interaction, kernel text/data mappings, and PAT CPU initialization.

## Risks And Edge Cases
Conflicting cacheability aliases can cause data corruption or machine checks. Range end semantics must be consistent. PAT write-protect support is CPU-dependent, and UC MTRR immunity must be honored.

## Test Signals
PAT selftests, ioremap/memremap cache-mode tests, driver WC mapping tests, and boot logs for PAT/MTRR setup provide signal.
