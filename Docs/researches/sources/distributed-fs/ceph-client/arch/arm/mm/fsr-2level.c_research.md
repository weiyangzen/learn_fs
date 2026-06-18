## sources/distributed-fs/ceph-client/arch/arm/mm/fsr-2level.c

### Purpose
Provides classic two-level ARM fault status decode tables for data aborts and instruction aborts.

### Important APIs, Types, And Functions
Defines static `fsr_info[]` and `ifsr_info[]` arrays of `struct fsr_info`, mapping FSR indices to handler function, signal, si_code, and diagnostic name. Handlers referenced include `do_bad`, `do_translation_fault`, `do_page_fault`, and `do_sect_fault`.

### Control Flow
Included directly by `fault.c` in non-LPAE builds. `do_DataAbort` and `do_PrefetchAbort` index these tables using `fsr_fs()` and dispatch to the selected handler; runtime initialization may patch entries with `hook_fault_code`.

### State, Dependencies, And Integration
The tables are mutable static state in `fault.c`'s compilation unit. They depend on signal constants and handler definitions visible before include. Integration is low-level ARM abort dispatch for short-descriptor page tables.

### Risks And Test Signals
Risks are wrong table index meanings, mismatched signal codes, and missing CPU-specific fault overrides. Test non-LPAE translation, permission, alignment, external abort, section fault, and prefetch abort cases plus boot-time `exceptions_init` patching.
