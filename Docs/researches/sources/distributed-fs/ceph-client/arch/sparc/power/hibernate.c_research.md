# sources/distributed-fs/ceph-client/arch/sparc/power/hibernate.c

Purpose: supplies SPARC64 C hooks for hibernation state save/restore and nosave-page detection.

Important APIs/types/functions: defines global `struct saved_context saved_context`, `pfn_is_nosave()`, `save_processor_state()`, and `restore_processor_state()`.

Control flow: `pfn_is_nosave()` converts `__nosave_begin`/`__nosave_end` to PFNs and tests whether a page belongs to the nosave section. `save_processor_state()` saves and clears FPU/VIS state. `restore_processor_state()` reloads TSB context state for `current->active_mm` using hardware context bits after image restore.

State and persistence: `saved_context` is populated by assembly suspend code. FPU state is saved in task/thread state, and TSB hardware state is restored after resume. Hibernation image persistence is handled by generic swsusp, not this file.

Dependencies and integration points: depends on generic suspend, `__nosave_*` section markers, VIS/FPU save helpers, `tsb_context_switch_ctx()`, and `mm->context` encoding.

Risks: failing to exclude nosave pages can corrupt restore. Missing FPU clear/save or TSB reload can resume with stale CPU/MMU state.

Test signals: hibernate/resume on sparc64 with active FPU users, validate nosave PFN exclusion, run memory checks after resume, and exercise processes with populated TSBs across hibernation.
