# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h

### Purpose
`mte.h` declares ARM64 Memory Tagging Extension page, thread, ptrace, suspend, and fault-check integration.

### Important APIs, Types, And Functions
Key APIs are `mte_clear_page_tags()`, tag copy to/from user, `mte_save_tags()`, `mte_restore_tags()`, tag storage allocation/free, `PG_mte_tagged`, page/folio tagging helpers, `mte_zero_clear_page_tags()`, `mte_sync_tags()`, `mte_copy_page_tags()`, thread init/switch, CPU setup, suspend enter/exit, `set_mte_ctrl()`, `get_mte_ctrl()`, `mte_ptrace_copy_tags()`, and TFSR check helpers.

### Control Flow
MM paths mark pages/folios tagged, synchronize tags when PTEs are installed, save/restore tags for swap or migration, and update task MTE state on context switch. Entry/exit paths check deferred tag faults when async modes are active.

### State, Persistence, And Dependencies
State includes page flags, tag storage buffers, task controls, CPU MTE registers, TFSR fault status, and swap-associated tag records. It depends on page flags, scheduler, KASAN enablement, PTE types, and `mte-def.h`.

### Integration Points
Used by memory management, swap, ptrace, KVM MTE, KASAN, and userspace ABI for tagged addresses.

### Risks
Tag storage lifetime must match page/swap lifetime. Page flag locking prevents double tagging. Deferred fault checks must not lose faults across context switch or suspend.

### Test Signals
Run MTE selftests, ptrace tag copy tests, swap/migration tag preservation, hugepage tagging, suspend/resume, and non-MTE config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte.h -->
