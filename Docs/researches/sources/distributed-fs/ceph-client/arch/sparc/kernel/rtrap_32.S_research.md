# sources/distributed-fs/ceph-client/arch/sparc/kernel/rtrap_32.S

Purpose: low-level SPARC32 return-from-trap path. It handles rescheduling, signal/notify work, buffered register windows, WIM/CWP manipulation, user stack validation, unaligned return PCs, and final `rett`.

Important APIs/symbols: exported labels include `ret_trap_entry`, `ret_trap_lockless_ipi`, `srmmu_rett_stackchk`, and runtime patch labels for 7-window or CPU-specific window-mask code. It calls `schedule`, `do_notify_resume`, `try_to_clear_window_buffer`, `do_memaccess_unaligned`, and `window_ret_fault`.

Control flow: the path first distinguishes kernel versus user returns via `PSR_PS`. User returns check `_TIF_NEED_RESCHED`, call `schedule`, then loop through `_TIF_DO_NOTIFY_RESUME_MASK` handling. If saved windows exist, it enables traps and asks C code to clear the buffer, then rechecks work. Otherwise it loads user outs, verifies there is a live user window or pulls one from the user stack by rotating `%wim`, validates stack alignment and address range, checks PC/NPC alignment, restores registers/Y/PSR, and executes `rett`. Kernel returns repair invalid windows if the return would hit WIM before restoring all registers.

State and persistence: mutates processor PSR, WIM, register windows, thread-info flags/counters, and saved trap-frame state. No persistent storage is involved.

Dependencies and integration points: depends on SPARC32 trap-frame layout, `thread_info` offsets, SRMMU/LEON MMU ASIs, window macros, scheduler, signal code, and setup-time patching for different window counts/CPU models.

Risks: interrupts/traps must be enabled and disabled in exact order around scheduler and user-memory window loads. Incorrect WIM rotation can corrupt register windows. Returning to unaligned PC/NPC must route to fault handling. User stack probing uses MMU status registers and must not expose kernel addresses.

Test signals: syscall/interrupt return to user with pending reschedule or signal, register-window overflow/underflow cases, bad user stack pointer, unaligned PC/NPC fault, kernel trap return with invalid window, LEON and sun4m/sun4d patched instruction paths.
