# sources/distributed-fs/ceph-client/arch/mips/kernel/relocate_kernel.S

## Purpose
Provides the kexec relocation trampoline that copies pages described by the kexec indirection page, synchronizes caches, coordinates secondary CPUs, and jumps to the new kernel.

## Important APIs, Types, and Functions
- `relocate_new_kernel` is the primary kexec relocation entry.
- `kexec_smp_wait` is the secondary CPU wait path under SMP.
- Exported data: `kexec_args`, `secondary_kexec_args`, `kexec_start_address`, `kexec_indirection_page`, and `relocate_new_kernel_size`.

## Control Flow
`relocate_new_kernel` loads new-kernel arguments into `a0-a3`, loads the indirection page and start address, and loops over entries. Entries tagged as destination update `s4`; indirection entries redirect the descriptor pointer; source entries copy one page word-by-word to the current destination; done entries break. On completion, SMP builds clear a relocated `kexec_flag` so waiting CPUs may proceed, synchronize caches (`syncw/synci` for Octeon, `sync` otherwise), and jump to `kexec_start_address`. `kexec_smp_wait` loads secondary arguments and start address, computes relocated `kexec_flag`, spins until primary clears it, performs a final sync/hook, and jumps.

## State and Persistence
Uses exported in-memory argument and control words populated by the kexec core. Copies physical/virtual page contents during shutdown; no persistent storage.

## Dependencies and Integration Points
Integrated with generic kexec machine code. Depends on MIPS kexec page-list flag conventions, register ABI, cache synchronization requirements, SMP stop/wait protocol, and optional platform `kexec_smp_wait_final`.

## Risks
The trampoline runs while the old kernel may be overwritten, so it must use only safe addresses and relocated flag computation. Incorrect interpretation of page flags corrupts the new kernel image. Cache sync is CPU-specific. Secondary CPUs must not jump before relocation is complete.

## Test Signals
`kexec -e` and crash-kdump boots should transfer control with correct arguments. SMP kexec should not leave secondaries spinning forever. New kernel instruction fetch should work immediately after relocation.
