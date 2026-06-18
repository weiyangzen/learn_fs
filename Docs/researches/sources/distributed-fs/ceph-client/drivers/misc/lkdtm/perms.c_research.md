# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/perms.c

## Purpose
`perms.c` validates kernel memory permission hardening: read-only data/text protections, non-executable data/stack/heap/vmalloc/user/null regions, user/kernel address separation, and function-descriptor write protection.

## Important APIs, Types, and Functions
Important routines include `execute_location()`, `execute_user_location()`, `setup_function_descriptor()`, `lkdtm_WRITE_RO()`, `lkdtm_WRITE_RO_AFTER_INIT()`, `lkdtm_WRITE_KERN()`, `lkdtm_WRITE_OPD()`, `lkdtm_EXEC_*()`, `lkdtm_ACCESS_USERSPACE()`, `lkdtm_ACCESS_NULL()`, and `lkdtm_perms_init()`. Static targets include `data_area`, `rodata`, `ro_after_init`, `do_nothing()`, and `do_overwritten()`.

## Control Flow
Write tests cast away protections and write into rodata, ro-after-init data, text, or function descriptors. Execution tests copy or reference a harmless return function into non-code regions and call through a function pointer. User/null tests map user memory or use NULL and then perform intentionally invalid kernel reads/writes. Initialization stores the real text address for `do_nothing()` and mutates `ro_after_init` while init-time writes are still allowed.

## State and Persistence
Static globals represent memory-section targets. `ro_after_init` transitions from writable during init to read-only after init. `do_nothing_ptr` preserves a runtime function pointer for later tests.

## Dependencies and Integration Points
Uses vmalloc, kmalloc, user mappings, `access_process_vm()`, cache flushing, architecture section/function-descriptor helpers, CFI annotations, and LKDTM crashtype registration.

## Risks
Architecture differences around function descriptors, instruction cache coherency, CFI/IBT, and MMU behavior can alter expected faults. Tests intentionally perform undefined or fatal operations.

## Test Signals
Expected signals are faults or panics on bad writes/executions/accesses, `XFAIL` for architectures without function descriptors, lack of `FAIL: survived` messages, and correct `ro_after_init` init-time mutation before final write test.
