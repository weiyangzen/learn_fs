## sources/distributed-fs/ceph-client/arch/arm/mm/fault.h

### Purpose
Defines ARM fault status register bit extraction and shared abort-handler prototypes.

### Important APIs, Types, And Functions
Defines `FSR_LNX_PF`, `FSR_CM`, `FSR_WRITE`, architecture-specific fault status encodings, `fsr_fs`, `is_translation_fault`, and `is_permission_fault`. Declares `do_bad_area`, `early_abt_enable`, `do_DataAbort`, and `do_PrefetchAbort`.

### Control Flow
Inline helpers decode either LPAE 6-bit FSR fields or classic 5-bit fields with split bit 10. Callers in `fault.c` use the predicates to choose page-fault, permission, execute, or oops paths.

### State, Dependencies, And Integration
No persistent state. Depends on bit macros and `CONFIG_ARM_LPAE`. It is shared by `fault.c` and `mmu.c` initialization paths.

### Risks And Test Signals
Risks are incorrect FSR masks when switching translation formats and signal misclassification. Test LPAE and non-LPAE abort cases, translation vs permission faults, write faults, and prefetch execute faults.
