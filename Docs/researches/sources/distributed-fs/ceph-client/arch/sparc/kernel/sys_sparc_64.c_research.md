# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_64.c

Purpose: implements sparc64-specific syscall helpers, mmap layout/range policy, SysV IPC demultiplexing, 32-bit personality handling, time adjustment ABI quirks, user trap installation, and memory-ordering control.

Important APIs/types/functions: `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `get_fb_unmapped_area()`, `arch_pick_mmap_layout()`, `sys_sparc_pipe()`, `sys_sparc_ipc()`, `sys_sparc64_personality()`, `sparc_mmap_check()`, `sys_mmap()`, `sys64_munmap()`, `sys64_mremap()`, `sys_nis_syscall()`, `sparc_breakpoint()`, `sys_getdomainname()`, `sys_sparc_adjtimex()`, `sys_sparc_clock_adjtime()`, `sys_utrap_install()`, `sys_memory_ordering()`, `sys_rt_sigaction()`, and `sys_kern_features()`.

Control flow: mmap code avoids the sparc64 VA hole, enforces 32-bit `STACK_TOP32` for compat tasks, color-aligns file/shared mappings, supports top-down 32-bit layout fallback, and offers framebuffer-friendly alignment. SysV IPC dispatches old multiplexed subcalls to generic semaphore/message/shared-memory helpers. `utrap_install()` validates trap type, manages per-thread shared/copy-on-write utrap arrays, returns old handlers, and installs new handlers. Time adjustment wrappers compensate for sparc64's 32-bit `tv_usec` field inside `__kernel_timex`.

State and persistence: modifies process mm layout, per-thread utrap pointer/refcount array, current `tstate` memory-model bits, personality flags, and normal syscall side effects. No direct filesystem persistence beyond delegated syscalls.

Dependencies and integration points: generic MM, hugetlb, SysV IPC, signal, POSIX time, personality, UTS, trap, context tracking, and SPARC thread flags.

Risks: `invalid_64bit_range()` is a hard ABI/security guard around the VA hole. Utrap copy-on-write refcounts are subtle. Time ABI overlays require exact structure interpretation. `sparc64_personality()` hides `PER_LINUX32` from userspace return values.

Test signals: 64-bit and 32-bit mmap placement around VA hole, MAP_FIXED shared alias rejection, framebuffer mmap alignment, SysV IPC subcalls, `utrap_install()` old/new/copy-on-write cases, `adjtimex`/`clock_adjtime` timeval layout, memory ordering model changes, and breakpoints from compat/native tasks.
