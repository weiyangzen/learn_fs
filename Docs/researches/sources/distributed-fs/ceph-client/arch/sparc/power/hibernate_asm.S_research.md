# sources/distributed-fs/ceph-client/arch/sparc/power/hibernate_asm.S

Purpose: implements SPARC64 low-level swsusp suspend and resume assembly paths.

Important APIs/functions: exports `swsusp_arch_suspend()` and `swsusp_arch_resume()`. Uses `saved_context` offsets for CWP, WSTATE, frame pointer, TICK, PSTATE, and selected global registers, and consumes `restore_pblist`.

Control flow: suspend saves register windows, current window state, tick/pstate, and global registers into `saved_context`, then calls `swsusp_save()` and unwinds two register windows. Resume flushes all TLBs, switches to physical ASI, walks the page backup list copying saved pages back to original physical addresses, restores saved register/window state, restores ASI, raises PIL, and returns zero.

State and persistence: writes CPU architectural state into `saved_context` and restores physical memory from the hibernation page list. No filesystem writes occur here.

Dependencies and integration points: depends on generic swsusp page lists, `__flush_tlb_all`, SPARC physical ASI operations, `asm-offsets.h`, and the C `saved_context` object.

Risks: the resume copy loop runs with special ASI/PIL settings and must use physical addresses correctly. Register-window restore ordering is critical. Wrong offsets corrupt CPU state after resume.

Test signals: hibernate/resume with register-window pressure, FPU/VIS users, memory checksum validation, TLB flush verification, and resume under different page-list lengths.
