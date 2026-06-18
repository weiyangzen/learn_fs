## sources/distributed-fs/ceph-client/arch/arm/mm/fsr-3level.c

### Purpose
Provides LPAE/three-level ARM fault status decode table for both data and instruction aborts.

### Important APIs, Types, And Functions
Defines static `fsr_info[]` with 64 entries and aliases `ifsr_info` to it. Entries map LPAE fault status values to `do_translation_fault`, `do_page_fault`, `do_bad`, signal numbers, si_codes, and names such as level translation, access flag, permission, external abort, parity error, debug event, and implementation faults.

### Control Flow
Included by `fault.c` when `CONFIG_ARM_LPAE` is enabled. Abort handlers index the shared table through the LPAE `fsr_fs()` helper.

### State, Dependencies, And Integration
The table is mutable inside the `fault.c` translation unit. Depends on LPAE FSR definitions and generic signal constants. Integration point is all LPAE abort dispatch.

### Risks And Test Signals
Risks include wrong 6-bit FSR entry mapping, using one table for instruction/data cases where future hardware differs, and signal-code mismatches. Test LPAE translation, permission, access flag, alignment, debug, external abort, and parity paths.
