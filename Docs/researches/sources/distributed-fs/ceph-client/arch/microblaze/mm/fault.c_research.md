# sources/distributed-fs/ceph-client/arch/microblaze/mm/fault.c

Purpose: handles heavyweight MicroBlaze page faults that assembly TLB miss handlers cannot resolve.

Important APIs and state: `do_page_fault()`, `bad_page_fault()`, private counters `pte_misses` and `pte_errors`, and `store_updates_sp()` for stack-growth validation.

Control flow: the handler stores EAR/ESR into regs, derives write/read fault state, handles disabled fault contexts, raises perf events, locks `mmap_lock`, locates/expands VMAs including stack guard checks, validates access permissions, calls `handle_mm_fault()`, handles retry/completed/error cases, and sends SIGSEGV/SIGBUS or calls kernel fixups/oops. `bad_page_fault()` uses exception tables before dying.

State and persistence: updates fault counters, `pt_regs`, VMA/page-table state through common mm, and user signals.

Dependencies and integration: called from `entry.S`; fast-path TLB handlers in `hw_exception_handler.S` fall back here.

Risks and test signals: instruction-fault write detection uses ESR bit patterns; stack growth has architecture-specific allowances. Test user read/write/exec faults, stack expansion, kernel uaccess fixups, OOM, SIGBUS mappings, and retry paths.
