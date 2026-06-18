# sources/distributed-fs/ceph-client/arch/arm/kernel/patch.c

Purpose: implements safe ARM kernel text patching for early boot and live SMP systems, including fixmap mapping and cache synchronization.

Important APIs/types/functions: `__patch_text`, `__patch_text_real`, `__patch_text_early`, `patch_text`, and `patch_text_array`. It maps target code through a fixmap slot when MMU protections require it.

Control flow: early patching writes directly and flushes I-cache. Live patching packages patch data, calls `stop_machine` or CPU-synchronized patching path, maps the page writable if needed, writes opcode(s), flushes D/I cache for the target range, and restores mapping.

State and persistence: kernel text is modified persistently. Temporary fixmap state is local to patch operations.

Dependencies and integration: used by jump labels, KGDB, ftrace, alternatives, module finalization, and branch generation helpers. Depends on cacheflush, fixmap, stop_machine/SMP coordination, and page attribute behavior.

Risks: patching executable text while other CPUs execute it requires exact synchronization; cache maintenance errors leave stale instructions. Test signals include live static key toggles under SMP, KGDB breakpoints, ftrace, module alternatives, and cache coherency stress.
