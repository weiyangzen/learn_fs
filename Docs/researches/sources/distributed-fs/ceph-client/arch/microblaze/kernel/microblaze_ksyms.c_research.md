# sources/distributed-fs/ceph-client/arch/microblaze/kernel/microblaze_ksyms.c

Purpose: exports selected MicroBlaze architecture helpers and libgcc routines to loadable modules.

Important APIs and state: exports `_mcount` under function tracing, `__copy_tofrom_user`, optional optimized `memcpy`/`memmove`, cache dispatch `mbc`, 32-bit arithmetic helpers (`__divsi3`, `__modsi3`, `__mulsi3`, `__udivsi3`, `__umodsi3`), and optional MB-manager APIs.

Control flow: compile-time configuration gates which symbols are visible. There is no runtime control flow beyond module symbol resolution.

State and persistence: exporting `mbc` exposes the global cache dispatch pointer to modules; other exports are pure functions or assembly service routines.

Dependencies and integration: must match objects selected by kernel/lib Makefiles. Modules relying on compiler-emitted libgcc calls need these symbols.

Risks and test signals: exporting an object not linked for a config breaks build; missing arithmetic exports break module relocation. Test module builds using division/multiplication, uaccess, optimized string routines, and ftrace.
