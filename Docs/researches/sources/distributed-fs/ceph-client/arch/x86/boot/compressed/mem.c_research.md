## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem.c

### Purpose
`compressed/mem.c` initializes and services early unaccepted-memory support for confidential-computing guests, accepting pages before decompression writes to them.

### Important APIs, Types, And Functions
Exports are `arch_accept_memory()` and `init_unaccepted_memory()`. The internal helper is `early_is_tdx_guest()`.

### Control Flow
`early_is_tdx_guest()` lazily checks CPUID for the TDX signature. `arch_accept_memory()` dispatches to `tdx_accept_memory()` for TDX, `snp_accept_memory()` for SEV-SNP, or halts for an unknown platform. `init_unaccepted_memory()` verifies EFI presence, retrieves EFI configuration table information, finds the Linux unaccepted-memory vendor table, validates version 1, and assigns the global `unaccepted_table` pointer.

### State, Persistence, And Dependencies
State includes cached TDX detection and the global `unaccepted_table` defined by EFI stub code. Dependencies include EFI helpers, TDX shared calls, SEV/SNP detection and acceptance, and boot params.

### Integration Points
`misc.c` calls `init_unaccepted_memory()` and, if true, `accept_memory(__pa(output), needed_size)` before decompression. EFI stub code may also initialize the table earlier, but this file reinitializes it for relocation cases.

### Risks
Calling acceptance on an unknown platform is fatal. CPUID detection happens before some later decompressor detection paths, so it must be safe for early users. Table version mismatch is fatal because memory-acceptance bitmap interpretation would be unsafe.

### Test Signals
Boot TDX with unaccepted memory, SEV-SNP with unaccepted memory, normal EFI without the table, non-EFI, bad table version, and relocation cases where EFI stub copied the image before setting the pointer.
