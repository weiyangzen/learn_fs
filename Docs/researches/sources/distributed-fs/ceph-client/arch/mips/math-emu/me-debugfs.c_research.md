# sources/distributed-fs/ceph-client/arch/mips/math-emu/me-debugfs.c

Purpose: exposes MIPS FPU emulator statistics through debugfs. It creates aggregate counter files and per-instruction counter files under `mips_debugfs_dir`, enabling runtime observability of software FPU emulation.

Important APIs/functions: defines per-CPU `fpuemustats`; `fpuemu_stat_get()` sums a selected `local_t` counter across online CPUs; `adjust_instruction_counter_name()` converts struct field underscores to dotted instruction names; `fpuemustats_clear_show()` zeroes many counters on the current CPU; `debugfs_fpuemu()` creates the debugfs tree.

Control flow: at `arch_initcall`, the file creates `fpuemustats`, a `fpuemustats_clear` file, aggregate stats, and an `instructions` subdirectory. `DEFINE_SIMPLE_ATTRIBUTE` and `DEFINE_SHOW_ATTRIBUTE` connect debugfs reads to counter aggregation/clear behavior.

State and persistence: state is per-CPU in-memory counters only. There is no persistence across reboot. The clear path writes only this CPU's counters, while reads aggregate online CPUs.

Dependencies and integration: depends on `asm/fpu_emulator.h` counter layout, `asm/debug.h` root directory, debugfs, cpumask iteration, and local counters.

Risks and test signals: clear-on-read is surprising and only clears the local CPU. Tests should mount debugfs, validate file names, check aggregate reads after emulated instructions, and verify no NULL debugfs root assumptions under disabled debugfs.
