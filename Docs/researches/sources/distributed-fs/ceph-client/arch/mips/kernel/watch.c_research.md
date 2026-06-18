## sources/distributed-fs/ceph-client/arch/mips/kernel/watch.c

Purpose: Manages MIPS hardware watchpoint registers for thread debug/watch support. It installs a thread's watch state on context switch, reads result bits for debugger consumption, clears hardware watch registers, and probes CPU watch capabilities.

Important APIs, types, and functions: `mips_install_watch_registers()` writes up to four usable watchlo/watchhi pairs from `task_struct.thread.watch.mips3264`. `mips_read_watch_registers()` reads watchhi result/mask bits into the current task. `mips_clear_watch_registers()` disables all probed watchlo registers, up to eight. `mips_probe_watch_registers()` discovers supported I/R/W and mask bits in `struct cpuinfo_mips`.

Control flow: Install and read functions use fallthrough switches keyed by `current_cpu_data.watch_reg_use_cnt`, so higher register counts cascade down to lower registers. Clear uses `watch_reg_count`, not use count, to wipe every implemented register and avoid repeat traps. Probe starts at watch0, writes test bits, reads back supported masks, follows the M bit chain to detect more registers, and caps actively used registers at four while counting up to eight.

State and persistence: State is split between per-thread saved watch arrays and per-CPU capability fields (`watch_reg_masks`, `watch_reg_count`, `watch_reg_use_cnt`). Hardware watch registers are volatile CP0 state restored/cleared by kernel control paths.

Dependencies and integration points: Relies on `asm/watch.h`, CP0 watch read/write helpers, `current_cpu_data`, and scheduler/debug code that calls install/read/clear. The user-visible behavior is mediated through ptrace/debug register handling elsewhere.

Risks: The functions call `BUG()` on unexpected counts, so bad CPU probing or corrupted state can crash the kernel. Only four registers are installed/read even if more exist; callers must respect that design. Release 1 CPUs that do not report result bits are handled by inferring conditions from watchlo, which is intentionally approximate.

Test signals: Exercise CPUs or emulators with 0, 1, 4, and 8 watch registers; ptrace watchpoint hits; context-switch save/restore; watch clear after exception; and old Release 1 behavior where watchhi condition bits are absent.
