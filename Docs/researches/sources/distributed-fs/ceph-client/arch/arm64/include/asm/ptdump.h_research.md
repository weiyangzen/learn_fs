# sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptdump.h` Defines page-table dumping state and callbacks for arm64 debugfs/kernel page-table inspection. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
arm64_ptdump_lock_key, struct addr_marker, ptdump_info, ptdump_prot_bits, ptdump_pg_level, ptdump_pg_state, ptdump_walk(), note_page*(), note_page_flush(), ptdump_debugfs_register(), EFI_RUNTIME_MAP_END. The file is 89 lines / 2846 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
When CONFIG_PTDUMP is enabled, walkers call note_page* callbacks per level; pg_state groups contiguous entries with identical protection and flushes the accumulated range when attributes or markers change. Disabled configs provide empty inline callbacks.

### State, Persistence, And Dependencies
State is temporary walk state in ptdump_pg_state, including current protection, range start, marker, W^X counts, and seq_file output. Debugfs registration persists only if configured. Depends on linux/ptdump.h, mm_types, seq_file, pgtable types; integrates with debugfs, kernel page-table walkers, W^X validation, and EFI runtime map display.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Incorrect grouping or level masks can hide W^X mappings or misreport page sizes; debugfs locking must avoid concurrent page-table mutation races.

### Test Signals
Enable CONFIG_PTDUMP/PTDUMP_DEBUGFS, compare dump output to known mappings, run W^X checks, and build disabled configs to validate stubs.
