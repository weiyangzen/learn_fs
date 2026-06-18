# subset-b-006026 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_debugger.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_debugger.c

## Purpose
This file is the KDB-to-KGDB bridge. It translates KGDB trap state into KDB reasons, initializes KDB's global current CPU/task/register context, removes and reinstalls KDB breakpoints around the interactive command loop, and returns the correct KGDB core action when KDB exits.

## Important APIs, Types, And Functions
`kdb_poll_funcs` exports the poll input chain, initially backed by `dbg_io_get_char`. `kdb_common_init_state()` and `kdb_common_deinit_state()` populate and clear `kdb_initial_cpu`, `kdb_current_task`, and `kdb_current_regs` from `kgdb_info`. `kdb_stub()` is the main KGDB callback. `kdb_gdb_state_pass()` forwards raw remote protocol state into `gdbstub_state()`.

## Control Flow
`kdb_stub()` records the current `kgdb_state`, classifies the entry reason from reentry state, breakpoint setup, NMI/oops/signo state, and the KDB breakpoint table, then removes KDB breakpoints before running `kdb_main_loop()`. If delayed software breakpoint single-step repair is already complete, it skips the user loop. On exit it either passes control to KGDB, reinstalls breakpoints, requests single-step or continue in the gdbstub state machine, handles CPU switch reentry, or returns the architecture-specific resume state.

## State, Persistence, And Dependencies
The persistent state is global debugger state, not filesystem state: `kdb_ks`, `kdb_initial_cpu`, `kdb_current_task`, `kdb_current_regs`, `KDB_STATE_*`, `KDB_FLAG(CATASTROPHIC)`, `kgdb_single_step`, `dbg_switch_cpu`, and entries in `kdb_breakpoints`. It depends on KGDB core state (`kgdb_active`, `kgdb_info`, `kgdb_arch_pc()`, `kgdb_arch_set_pc()`, `gdbstub_state()`), KDB breakpoint helpers, and CPU/NMI helpers.

## Integration Points
This is entered by the KGDB core when KDB is selected as the frontend. It calls into `kdb_main_loop()` in `kdb_main.c`, breakpoint management in the KDB breakpoint file, and KGDB debug core internals from `debug_core.h`.

## Risks
Incorrect reason classification can either swallow a non-KDB trap or expose the interactive debugger on the wrong event. Breakpoint delay state is delicate: failing to set or clear `SSBPT`/`DOING_SS` correctly can leave patched instructions or repeated traps. Catastrophic detection relies on every online CPU's `enter_kgdb` state, so stuck CPUs force conservative behavior. `kdb_ks` is a global pointer valid only while in the debugger.

## Test Signals
Useful signals are keyboard entry, system NMI entry, oops entry, software breakpoint hit and continue, single-step over breakpoint, `kgdb` command transition, and `cpu` command switching back through `DBG_SWITCH_CPU_EVENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_debugger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_io.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_io.c

## Purpose
This file implements KDB console input and output independent of the architecture. It polls debugger consoles, handles line editing, command history control characters, symbol completion, KGDB remote protocol transition detection, pager prompts, `| grep` output filtering, optional printk logging, and multi-console writes while CPUs are stopped.

## Important APIs, Types, And Functions
`kdb_getchar()` polls `kdb_poll_funcs` and decodes VT100 escape sequences into KDB control codes. `kdb_getstr()` prints the prompt and delegates to `kdb_read()`. `kdb_read()` owns line editing, tab completion through `kallsyms_symbol_complete()` and `kallsyms_symbol_next()`, and special `$?#3f`/`$qSupported` KGDB handoff. `vkdb_printf()` and `kdb_printf()` format output, apply grep and pager behavior, write through `dbg_io_ops`, and optionally mirror output to printk. `kdb_msg_write()` writes to the active KGDB console and other usable consoles.

## Control Flow
Input loops over all registered poll functions, touching the NMI watchdog on each full pass. Escape bytes are accumulated with a two-second polling delay to distinguish bare ESC from arrow/home/end/delete sequences. `kdb_read()` edits the in-memory command buffer, redraws the prompt as needed, completes symbols on the first tab, lists matching symbols on the second tab, and returns complete lines or history control markers. Output is buffered through a 256-byte static buffer; when grep mode is active, complete newline-terminated lines are searched before emission. Pager state increments `kdb_nextline` and prompts once the configured line count is reached.

## State, Persistence, And Dependencies
State includes `kdb_prompt_str`, `kdb_trap_printk`, `kdb_printf_cpu`, `kdb_buffer`, grep accumulation pointers, `suspend_grep`, `kdb_nextline`, `KDB_STATE(PAGER)`, `KDB_STATE(KGDB_TRANS)`, and `KDB_FLAG(CMD_INTERRUPT)`. There is no durable persistence. Dependencies include KGDB I/O ops, console SRCU/NBCON APIs, `printk`, kallsyms, SMP CPU identity, NMI watchdog, and KDB environment variables such as `LINES`, `COLUMNS`, `LOGGING`, `MOREPROMPT`, `SEARCHPROMPT`, and `DTABCOUNT`.

## Integration Points
`kdb_main.c` calls `kdb_getstr()` for commands and most KDB code uses exported `kdb_printf()`. The KGDB transition path calls `kdb_gdb_state_pass()` in `kdb_debugger.c`. Symbol completion depends on `kdb_support.c` wrappers over kallsyms.

## Risks
The output lock is a CPU-owner compare-exchange, so recursive output from the same CPU is tolerated but other CPUs spin with interrupts disabled. Console writes are deliberately reentrant under debugger conditions and rely on selected console drivers tolerating that. Grep buffers can hold partial lines until a newline or prompt. The input path is polling-only with interrupts off, so long escape delays and pager waits are expected but can surprise automation.

## Test Signals
Exercise CR/LF normalization, arrow keys, home/end/delete, tab completion, double-tab listing, KGDB remote `$` packets, `cmd | grep pattern`, `/` search at the pager prompt, `q` pager interruption, `LOGGING=1`, and output on NBCON and classic consoles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_keyboard.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_keyboard.c

## Purpose
This file provides the i8042/PC keyboard polling backend for KDB. It reads raw keyboard controller registers while the debugger is active, translates scancodes into printable characters or KDB line-editing control codes, and cleans up ENTER release codes before returning control to the normal kernel input path.

## Important APIs, Types, And Functions
`kdb_get_kbd_char()` is the exported poll function. It uses `KBD_STATUS_REG`, `KBD_DATA_REG`, `KBD_STAT_OBF`, and `KBD_STAT_MOUSE_OBF`, tracks static shift/caps/ctrl state, reads `plain_map` and `key_maps`, and returns ASCII/control values. `kdb_kbd_cleanup_state()` drains pending ENTER/KP ENTER break sequences after KDB exits.

## Control Flow
The poller first refuses operation when i8042 or VT console use is disabled, or when the controller appears absent. It returns `-1` when no output byte exists, when the byte is mouse input, or when it only updates modifier state. It ignores key releases except for shift/control bookkeeping and ENTER cleanup. Printable keys come from the plain, shifted, or control keymap, while tab/delete/home/end/arrows are mapped to KDB control characters consumed by `kdb_read()`.

## State, Persistence, And Dependencies
Persistent in-memory state includes `kbd_exists`, `kbd_last_ret`, and static modifier variables in `kdb_get_kbd_char()`. `kbd_last_ret` tells cleanup whether KDB processed ENTER and should absorb the corresponding break code. Dependencies are low-level port I/O, Linux keyboard maps, KDB flags `NO_I8042` and `NO_VT_CONSOLE`, and optional LED toggling under `KDB_BLINK_LED`.

## Integration Points
When enabled, this function is registered in KDB's poll function chain and feeds `kdb_getchar()` in `kdb_io.c`. `kdb_main_loop()` calls `kdb_kbd_cleanup_state()` on exit through the private header abstraction.

## Risks
The cleanup loop spins until it sees the expected ENTER break scancode; unusual controller behavior or mashed-key cases can prolong debugger exit. Only a subset of keys is accepted, nonprintables are dropped, and the translation assumes PC set-1 style scancodes. Mouse bytes must be skipped correctly or they can corrupt KDB input.

## Test Signals
Use direct keyboard debugger entry, printable keys, shift/caps/control combinations, arrows/home/end/delete/tab/backspace, repeated ENTER, keypad ENTER, mouse activity during KDB, and exits after `go` to confirm no ENTER break leaks into the normal console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_main.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_main.c

## Purpose
This is KDB's architecture-independent command engine. It owns command registration, command parsing, environment variables, command history, macro definitions, lockdown-aware command permissions, the per-CPU main debugger loop, and the built-in commands for memory, registers, process state, CPU switching, dmesg, sysrq, reboot, signals, system summary, and per-CPU data.

## Important APIs, Types, And Functions
Global state includes `kdb_flags`, `kdb_state`, `kdb_initial_cpu`, `kdb_current_task`, `kdb_current_regs`, grep globals, command history buffers, and the `kdb_cmds_head` list. Important helpers are `kdbgetenv()`, `kdbgetintenv()`, `kdb_set()`, `kdbgetaddrarg()`, `kdb_parse()`, `kdb_local()`, `kdb_main_loop()`, `kdb_register()`, `kdb_register_table()`, `kdb_unregister()`, and `kdb_init()`. Built-in command handlers include `kdb_md()`, `kdb_mm()`, `kdb_go()`, `kdb_rd()`, `kdb_rm()`, `kdb_dmesg()`, `kdb_cpu()`, `kdb_ps()`, `kdb_pid()`, `kdb_kgdb()`, `kdb_help()`, `kdb_kill()`, `kdb_summary()`, and `kdb_per_cpu()`.

## Control Flow
`kdb_main_loop()` waits while this CPU is held as a slave, exits if another CPU is leaving, otherwise calls `kdb_local()`. `kdb_local()` prints the entry reason, checks lockdown, then repeatedly prompts through `kdb_getstr()`, handles command history controls, parses commands, reports diagnostics, and breaks on `go`, CPU switch, single-step, or KGDB transition. `kdb_parse()` tokenizes in place, handles comments, `| grep`, macros, command abbreviation, permission checks, command repeat semantics, and address-expression fallback. Initialization registers the built-in table, initializes breakpoints, and replays boot-time `kdb_cmds`.

## State, Persistence, And Dependencies
KDB environment values live in the fixed `__env[31]` table and may allocate replacement strings. Macros allocate `struct kdb_macro` and statement strings. Memory display remembers last address/radix/width/repeat. Command history is a 32-entry static ring. Security state is derived from `kdb_cmd_enabled` and kernel lockdown checks. Dependencies include kallsyms, KGDB per-CPU state, ptrace register definitions, scheduler/task iteration, printk/kmsg dump, sysrq, reboot, signals, sysinfo, CPU masks, and KDB support routines for safe memory/symbol access.

## Integration Points
`kdb_debugger.c` enters `kdb_main_loop()`. `kdb_io.c` supplies command I/O and grep output behavior. `kdb_support.c` supplies symbol lookup, memory reads/writes, and task-state formatting. Other KDB files register commands through the exported registration functions.

## Risks
The parser uses static `argv` and `cbuf`, so recursive parse paths must avoid using old argument pointers. Command permission masks are security-sensitive, especially memory/register read/write and flow control under lockdown. Memory write/register write commands can alter a live kernel. Macro definition allocates memory in debugger context and must force-close incomplete `defcmd` blocks. CPU switching and catastrophic continue behavior depend on precise KDB state flags.

## Test Signals
Cover command abbreviation and repeat, `set`/`env`, `KDBDEBUG`, `defcmd`/`endefcmd`, address parsing with symbols/env/offsets, `md` variants including physical and symbolic reads, `mm`, `go` on initial versus non-initial CPU, `cpu`, `pid`, `ps` filters, `dmesg` ranges, sysrq, `kill`, lockdown permission denial, and transition to KGDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_private.h -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_private.h

## Purpose
This header is the private contract shared by KDB implementation files. It defines internal command return codes, diagnostic/debug flags, machine-format strings, breakpoint structures, symbol table metadata, KDB state bits, helper macros for safe memory access, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important definitions include `KDB_CMD_GO`, `KDB_CMD_CPU`, `KDB_CMD_SS`, `KDB_CMD_KGDB`, `KDB_DEBUG_*`, `KDB_MAXBPT`, `kdb_symtab_t`, `kdb_bp_t`, `kdb_dbtrap_t`, `KDB_STATE_*`, `KDB_STATE()`, `KDB_STATE_SET()`, `KDB_STATE_CLEAR()`, `KDB_SP_*`, `KDB_TSK()`, `KDB_TSKREGS()`, `GFP_KDB`, and `KDB_WORD_SIZE`. It declares the memory helpers, symbol helpers, parser helpers, command registration, breakpoint management, I/O functions, task-state helpers, and current task/register globals.

## Control Flow
There is no runtime control flow in the header, but its constants define how control flows between files. Command handlers return negative `KDB_CMD_*` values to the main loop. State bits steer debugger ownership, pager behavior, single stepping, KGDB transition, CPU hold/reentry, and keyboard entry. Memory helper macros expand variable arguments into size-aware safe-copy calls.

## State, Persistence, And Dependencies
The header exposes shared in-memory state in `kdb_state`, `kdb_nextline`, `kdb_current_task`, `kdb_current_regs`, `kdb_breakpoints`, grep globals, and prompt storage. It depends on `linux/kgdb.h` and KGDB debug core internals, so it is private to the KGDB/KDB implementation and not a stable external API.

## Integration Points
All KDB implementation files include this header. It links `kdb_debugger.c`, `kdb_main.c`, `kdb_io.c`, `kdb_keyboard.c`, support code, breakpoint code, and backtrace/module commands. It also hides optional keyboard cleanup behind a no-op macro when `CONFIG_KDB_KEYBOARD` is disabled.

## Risks
State bits are global and untyped; adding or reusing bits incorrectly can break debugger control flow. The safe memory macros take variables rather than pointers, which is convenient but easy to misuse if callers expect pointer semantics. `GFP_KDB` must match debugger context because sleeping allocation while the debug master is active can be unsafe.

## Test Signals
Build coverage across 32-bit and 64-bit architectures checks format strings and word sizes. Config combinations should include `CONFIG_KGDB_KDB`, keyboard enabled/disabled, and architectures with varying register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_support.c -->
# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_support.c

## Purpose
This file provides KDB's shared support routines for symbol lookup/printing, symbol completion, debugger-safe memory access, physical memory reads, string duplication, and task-state formatting.

## Important APIs, Types, And Functions
`kdbgetsymval()` resolves exact symbols through kallsyms. `kdbnearsym()` resolves nearest symbols and fills `kdb_symtab_t`. `kallsyms_symbol_complete()` and `kallsyms_symbol_next()` support tab completion. `kdb_symbol_print()` formats addresses with optional symbol/module/offset metadata. `kdb_strdup()` and `kdb_strdup_dequote()` allocate KDB-owned strings. `kdb_getarea_size()`, `kdb_putarea_size()`, `kdb_getphysword()`, `kdb_getword()`, and `kdb_putword()` implement safe memory access. `kdb_task_state_char()` and `kdb_task_state()` format/filter tasks for `ps`/backtrace commands.

## Control Flow
Symbol lookup zeroes the result, queries kallsyms, and suppresses absurd nearest-symbol offsets. Completion walks kallsyms to count matches and extend the prefix to the longest common prefix. Memory reads and writes use `copy_from_kernel_nofault()` and `copy_to_kernel_nofault()`, setting `KDB_STATE(SUPPRESS)` after the first bad-address message. Physical reads validate PFNs and temporarily map pages with `kmap_local_page()`. Task state maps idle tasks to `-` when appropriate and sleeping kernel daemons to lowercase state characters.

## State, Persistence, And Dependencies
State is limited to static kallsyms completion buffers and KDB suppress/debug flags. No persistent storage exists. Dependencies include kallsyms walking, nofault copy helpers, highmem mapping, page/PFN helpers, scheduler state, `kgdb_info`, and private KDB formatting constants.

## Integration Points
`kdb_main.c` uses these helpers for address parsing, memory display/modify, process listing, per-CPU display, and diagnostics. `kdb_io.c` uses completion helpers. Other KDB commands can use the exported symbol and memory helpers.

## Risks
`kdbnearsym()` uses a static name buffer and relies on KDB's single-master execution model. Physical reads assume the requested width does not cross problematic boundaries. Bad-address suppression avoids log spam but may hide repeated faults after the first message until a successful access clears it. `kdb_putword()` can write arbitrary kernel memory when permissions allow it.

## Test Signals
Test exact and nearest symbol lookup, tab completion with no/one/many matches, bad virtual and physical addresses, 1/2/4/8-byte reads and writes, highmem physical reads, task filters with idle/system-daemon states, and `md`/`mm` callers under `KDB_STATE(SUPPRESS)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/delayacct.c -->
# sources/distributed-fs/ceph-client/kernel/delayacct.c

## Purpose
This file implements per-task delay accounting for CPU scheduler delay, block I/O, swap-in, free-page reclaim, thrashing, compaction, write-protect copy, and IRQ time. It feeds taskstats and exposes a sysctl to enable or disable the static-key guarded accounting path.

## Important APIs, Types, And Functions
Global state includes `delayacct_key`, `delayacct_on`, and `delayacct_cache`. `delayacct_init()` creates the `task_delay_info` cache and initializes `init_task`. `__delayacct_tsk_init()` allocates per-task delay state. `delayacct_add_tsk()` copies accounting into `struct taskstats`. Start/end pairs include block I/O, freepages, thrashing, swapin, compaction, and wpcopy. `__delayacct_irq()` accumulates IRQ delay. `__delayacct_blkio_ticks()` returns block delay in clock ticks.

## Control Flow
Boot option `delayacct` sets `delayacct_on`, then `delayacct_init()` installs the static key according to that setting. The sysctl handler validates admin permission on writes, parses a 0/1 value, and calls `set_delayacct()`. Each end function computes elapsed nanoseconds from `local_clock()`, updates totals/counts/min/max under the task delay raw spinlock, and records wall-clock timestamps when a new max occurs. `delayacct_add_tsk()` snapshots CPU and scheduler stats, then locks `tsk->delays` to merge delay buckets.

## State, Persistence, And Dependencies
All state is per-task memory from `delayacct_cache` plus the global static key. There is no durable persistence. Dependencies include scheduler cputime and sched_info, `taskstats`, sysctl, capabilities, slab cache allocation, raw spinlocks, `local_clock()`, and `ktime_get_real_ts64()`.

## Integration Points
Scheduler, block, reclaim, swap, compaction, memory-management, and IRQ accounting paths call the exported delayacct hooks through `linux/delayacct.h`. Userspace observes results through taskstats and toggles accounting with `/proc/sys/kernel/task_delayacct` when proc sysctl is enabled.

## Risks
Overflow handling zeros totals when additions wrap, so consumers must interpret zero total with nonzero count as overflow. Several CPU scheduler fields are sampled without locking by design. Start/end imbalance can produce bogus delays. Allocation failure for a task leaves `tsk->delays` NULL, and callers must be guarded by the delayacct static key/macros.

## Test Signals
Test boot-time enable, sysctl permission and min/max parsing, taskstats output under I/O wait, swap/reclaim/compaction workloads, nested thrashing state suppression, IRQ delay accounting, and overflow behavior under synthetic large counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/delayacct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma.c -->
# sources/distributed-fs/ceph-client/kernel/dma.c

## Purpose
This legacy file manages reservation of ISA-style DMA channels and exposes channel ownership through `/proc/dma` when procfs is enabled. It provides `request_dma()` and `free_dma()` for architectures that define `MAX_DMA_CHANNELS`, and harmless stubs otherwise.

## Important APIs, Types, And Functions
`DEFINE_SPINLOCK(dma_spin_lock)` exports the legacy DMA lock. `struct dma_chan` stores a busy flag and `device_id`. `request_dma()` reserves a channel with `xchg()`. `free_dma()` releases it and warns on invalid or double-free attempts. `proc_dma_show()` prints busy channels or `No DMA`. `proc_dma_init()` creates `/proc/dma`.

## Control Flow
With `MAX_DMA_CHANNELS`, channel 4 starts reserved as `cascade`. `request_dma()` rejects out-of-range channel numbers, atomically swaps the lock to busy, and records the device name. `free_dma()` validates range and atomically clears the busy flag. Procfs iteration prints every busy channel and associated owner. Without `MAX_DMA_CHANNELS`, requests fail with `-EINVAL` and frees are no-ops.

## State, Persistence, And Dependencies
State is the static `dma_chan_busy[]` array and exported `dma_spin_lock`. It is not persistent across boot. Dependencies include architecture `asm/dma.h`, procfs, seq_file, `xchg()`, and kernel warning/printk support.

## Integration Points
Legacy drivers call `request_dma()`/`free_dma()` directly. Procfs consumers read `/proc/dma`. The symbols are exported for modules.

## Risks
The `device_id` pointer is stored, not copied, so callers must pass storage that remains valid while the channel is reserved. `free_dma()` does not clear `device_id`, but proc output is gated by the busy flag. Drivers must follow the documented IRQ-then-DMA acquisition order to reduce resource deadlocks.

## Test Signals
Test valid reservation/free, duplicate reservation returning `-EBUSY`, out-of-range request returning `-EINVAL`, double free warning, channel 4 reserved by default, stub behavior on architectures without `MAX_DMA_CHANNELS`, and `/proc/dma` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/dma/Kconfig

## Purpose
This Kconfig file defines the kernel DMA mapping framework feature switches. It controls whether DMA exists, which helper implementations build, architecture capability flags, SWIOTLB behavior, restricted pools, coherent pools, CMA, DMA API debugging, and the DMA map benchmark debugfs driver.

## Important APIs, Types, And Functions
Key symbols are `HAS_DMA`, `DMA_OPS_HELPERS`, `DMA_OPS_BYPASS`, `ARCH_HAS_DMA_MAP_DIRECT`, `NEED_*` scatterlist/map-state flags, `ARCH_DMA_ADDR_T_64BIT`, sync/prep/unencrypted/batched architecture flags, `ARCH_DMA_DEFAULT_COHERENT`, `SWIOTLB`, `SWIOTLB_DYNAMIC`, `DMA_NEED_SYNC`, `DMA_RESTRICTED_POOL`, `DMA_NONCOHERENT_MMAP`, `DMA_COHERENT_POOL`, `DMA_GLOBAL_POOL`, `DMA_DIRECT_REMAP`, `ARCH_HAS_DMA_ALLOC`, `DMA_CMA`, `DMA_NUMA_CMA`, CMA sizing choices, `DMA_API_DEBUG`, and `DMA_MAP_BENCHMARK`.

## Control Flow
The file is declarative. Symbol selections and dependencies drive compilation in `kernel/dma/Makefile` and conditional code in the DMA implementation files. CMA size choice selects megabytes, percentage, minimum, or maximum. Debug and benchmark options expose runtime instrumentation when selected.

## State, Persistence, And Dependencies
Configuration state is persisted in the kernel build `.config`. Several symbols select helper requirements, such as `DMA_API_DEBUG` and `SWIOTLB` selecting map state. Device-tree restricted pools depend on OF reserved memory and SWIOTLB. CMA depends on `HAVE_DMA_CONTIGUOUS` and `CMA`; benchmark depends on `DEBUG_FS`.

## Integration Points
These symbols gate `coherent.c`, `contiguous.c`, `debug.c`, `direct.c`, `dummy.c`, `map_benchmark.c`, and other DMA files not in this work item. Architecture Kconfigs select capability symbols to choose direct mapping, arch allocation hooks, cache sync hooks, and coherent defaults.

## Risks
Incorrect selects can compile incompatible paths, for example non-coherent mmap without page-table support or global coherent pools on architectures that require uncached setup. Enabling `DMA_API_DEBUG` is intentionally expensive. CMA sizing can reserve too much or too little early memory. Restricted pools require careful device-tree descriptions.

## Test Signals
Build matrix coverage should include no-DMA, direct-DMA, SWIOTLB, non-coherent, CMA, NUMA CMA, DMA API debug, and benchmark configurations. Runtime signals include successful boot, expected debugfs nodes, CMA reservation logs, and DMA mapping selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/Makefile -->
# sources/distributed-fs/ceph-client/kernel/dma/Makefile

## Purpose
This Makefile maps DMA Kconfig symbols to object files in `kernel/dma`. It is the build integration point that selects direct mapping, ops helpers, dummy ops, CMA, coherent memory, debug instrumentation, SWIOTLB, coherent pools, remapping, and map benchmarking.

## Important APIs, Types, And Functions
Object selections include `mapping.o direct.o` for `CONFIG_HAS_DMA`, `ops_helpers.o` for `CONFIG_DMA_OPS_HELPERS`, `dummy.o` for `CONFIG_ARCH_HAS_DMA_OPS`, `contiguous.o` for `CONFIG_DMA_CMA`, `coherent.o` for `CONFIG_DMA_DECLARE_COHERENT`, `debug.o` for `CONFIG_DMA_API_DEBUG`, `swiotlb.o` for `CONFIG_SWIOTLB`, `pool.o` for `CONFIG_DMA_COHERENT_POOL`, `remap.o` for `CONFIG_MMU`, and `map_benchmark.o` for `CONFIG_DMA_MAP_BENCHMARK`.

## Control Flow
Kbuild evaluates each `obj-$(CONFIG_*)` expression and links the corresponding object into the kernel or module build according to configuration. There is no runtime behavior.

## State, Persistence, And Dependencies
The only state is build configuration. It depends on Kconfig symbols defined in `kernel/dma/Kconfig` and architecture Kconfig files.

## Integration Points
This file connects the generic DMA framework source files to the kernel build. It must stay aligned with declarations in `linux/dma-map-ops.h`, `linux/dma-direct.h`, and feature guards inside the C files.

## Risks
Missing object selection causes unresolved symbols or silent loss of configured functionality. Over-selection can build code whose assumptions are not met by the architecture. Ordering is mostly not semantic, but `mapping.o direct.o` are paired for `HAS_DMA`.

## Test Signals
Build tests for each relevant `CONFIG_*` combination are the main signal, especially `HAS_DMA=n`, `ARCH_HAS_DMA_OPS=y`, `DMA_CMA=y`, `DMA_DECLARE_COHERENT=y`, `DMA_API_DEBUG=y`, `SWIOTLB=y`, and `DMA_MAP_BENCHMARK=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/coherent.c -->
# sources/distributed-fs/ceph-client/kernel/dma/coherent.c

## Purpose
This file implements reserved coherent DMA memory pools, both per-device and optional global pools. It lets platform or device-tree code declare memory regions that `dma_alloc_coherent()` can allocate from, and supports freeing and mmap of allocations from those pools.

## Important APIs, Types, And Functions
`struct dma_coherent_mem` stores virtual base, device DMA base, PFN base, page count, bitmap, spinlock, and whether device DMA PFN offset should be used. Public APIs include `dma_declare_coherent_memory()`, `dma_release_coherent_memory()`, `dma_alloc_from_dev_coherent()`, `dma_release_from_dev_coherent()`, `dma_mmap_from_dev_coherent()`, and optional global-pool helpers. Device-tree hooks are `rmem_dma_setup()`, `rmem_dma_device_init()`, and `rmem_dma_device_release()`.

## Control Flow
Initialization remaps the physical range with write-combining attributes, allocates a bitmap, and assigns the pool to a device or global pointer. Allocation finds a free bitmap region of the requested order under a spinlock, computes DMA and CPU addresses, unlocks, and zeroes memory. Release validates the virtual address range and releases the bitmap region. Mmap checks that the requested VMA fits inside the allocation before calling `remap_pfn_range()`. Reserved-memory setup rejects reusable pools and records `linux,dma-default` for global coherent memory when configured.

## State, Persistence, And Dependencies
Per-device state is `dev->dma_mem`; global state is `dma_coherent_default_memory` and early reserved-memory base/size. Pool allocation state is a bitmap protected by a spinlock. Dependencies include memremap/memunmap, bitmap allocation, device DMA masks, `phys_to_dma()`, reserved-memory OF hooks, and VMA remapping.

## Integration Points
Direct DMA allocation and mmap paths consult these helpers before falling back to generic pages. Device tree `shared-dma-pool` regions bind devices to coherent pools through reserved memory ops. `CONFIG_DMA_GLOBAL_POOL` provides a default pool for non-coherent direct allocations.

## Risks
Only one coherent pool can be assigned to a device. Pool size is stored as an `int` number of pages. Range checks must prevent mmap outside the pool. Reserved memory beyond a device mask only warns, so a misconfigured platform can still fail later. Global pool initialization depends on early reserved-memory discovery order.

## Test Signals
Test per-device declare/allocate/free/mmap/release, overlapping double assignment returning `-EBUSY`, allocation exhaustion, device mask warnings, global `linux,dma-default`, and reserved-memory attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/coherent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/contiguous.c -->
# sources/distributed-fs/ceph-client/kernel/dma/contiguous.c

## Purpose
This file integrates the Contiguous Memory Allocator with DMA allocation. It reserves global, per-device, and optional NUMA CMA regions during early boot and provides allocation/free helpers used by the direct DMA allocator.

## Important APIs, Types, And Functions
Important state includes `dma_contiguous_areas[]`, `dma_contiguous_default_area`, command-line CMA size/base/limit values, and optional NUMA CMA arrays. Public APIs include `dma_contiguous_get_area_by_idx()`, `dev_get_cma_area()`, `dma_contiguous_reserve()`, `dma_contiguous_reserve_area()`, `dma_alloc_from_contiguous()`, `dma_release_from_contiguous()`, `dma_alloc_contiguous()`, and `dma_free_contiguous()`. Device-tree hooks include `rmem_cma_validate()`, `rmem_cma_fixup()`, `rmem_cma_setup()`, and device init/release callbacks.

## Control Flow
Early parameters parse `cma=`, `numa_cma=`, and `cma_pernuma=`. `dma_contiguous_reserve()` reserves NUMA CMA areas first, then chooses the default size from command line or Kconfig and declares a default CMA region if needed. Device-tree `shared-dma-pool` regions that are reusable and not `no-map` become CMA areas; `linux,cma-default` selects the default unless overridden by `cma=`. Allocation tries a device-specific CMA area, skips CMA for single-page generic allocations, tries per-NUMA areas when configured, then falls back to the default CMA area. Free releases to the matching device, NUMA, or default CMA area, then falls back to buddy freeing.

## State, Persistence, And Dependencies
CMA regions are persistent for the boot lifetime. Early command-line data is `__initdata`. Dependencies include memblock/CMA core, OF reserved memory, NUMA node state, device `cma_area`, and architecture `dma_contiguous_early_fixup()`.

## Integration Points
`dma_direct_alloc()` and related direct DMA paths call `dma_alloc_contiguous()` and `dma_free_contiguous()`. Reserved-memory device attachment populates `dev->cma_area`. CMA areas can be enumerated by index for heap creation or other subsystem integration.

## Risks
Early reservation failures reduce or remove CMA availability. Alignment is constrained by `CONFIG_CMA_ALIGNMENT` and `CMA_MIN_ALIGNMENT_BYTES`. Command-line `cma=` intentionally overrides device-tree default CMA. Single-page allocations bypass generic CMA, which is intentional but can surprise tests expecting all DMA pages from CMA.

## Test Signals
Test `cma=0`, fixed and ranged `cma=size@base-limit`, default Kconfig sizing modes, per-NUMA and node-specific CMA parameters, DT reusable shared pools, invalid alignment rejection, device-specific allocation, fallback order, and free fallback to buddy pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/contiguous.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/debug.c -->
# sources/distributed-fs/ceph-client/kernel/dma/debug.c

## Purpose
This file implements DMA API misuse detection. It tracks live DMA mappings and coherent/noncoherent allocations, verifies unmap/sync/free parameters, detects mapping of illegal memory, tracks unchecked `dma_mapping_error()` results, reports leaks on driver unbind, and exposes debugfs controls and dumps.

## Important APIs, Types, And Functions
`struct dma_debug_entry` records device, DMA address, size, type, direction, scatterlist counts, physical address, map-error state, cacheline-clean state, and optional stack trace. Core helpers include hash bucket lookup/add/delete, `active_cacheline_insert()`/`remove()`, `dma_entry_alloc()`/`free()`, `add_dma_entry()`, `check_unmap()`, `check_sync()`, `check_sg_segment()`, `check_for_stack()`, and `check_for_illegal_area()`. Public hooks include `debug_dma_map_single()`, `debug_dma_map_phys()`, `debug_dma_mapping_error()`, `debug_dma_unmap_phys()`, `debug_dma_map_sg()`, `debug_dma_unmap_sg()`, coherent alloc/free hooks, sync hooks, noncoherent page alloc/free hooks, `debug_dma_dump_mappings()`, and `dma_debug_add_bus()`.

## Control Flow
`dma_debug_init()` initializes hash buckets and preallocates entries at core init unless disabled by `dma_debug=off`. Mapping hooks allocate entries, validate stack/text/rodata/SG segment rules, then add entries to a DMA-address hash and active-cacheline radix tree. Unmap/free hooks build a reference entry, locate a best-fit match, verify size/type/direction/SG count/CPU address and map-error checks, then remove and free the entry. Sync hooks locate a containing mapping and verify range and direction. Debugfs exposes error counts, free-entry counters, driver filtering, and a mapping dump. Bus notifiers report live mappings when drivers unbind.

## State, Persistence, And Dependencies
Global state includes `dma_entry_hash[16384]`, `free_entries`, `global_disable`, `dma_debug_initialized`, error display counters, preallocation counts, driver filter state, and the active-cacheline radix tree. It persists only for the boot. Dependencies include DMA mapping APIs, scatterlists, stacktrace, debugfs, bus notifiers, SWIOTLB, sections bounds, vmalloc/usercopy helpers, radix tree, and spinlocks.

## Integration Points
Generic DMA mapping wrappers call these hooks when `CONFIG_DMA_API_DEBUG` is enabled; `debug.h` provides no-op stubs otherwise. Debugfs creates `/sys/kernel/debug/dma-api/*`. Bus types call `dma_debug_add_bus()` to get unbind leak checks.

## Risks
Instrumentation is expensive and can disable itself on allocation failure or cacheline tracking ENOMEM. Error counters are intentionally racy because debugfs exposes them directly. Hashing by DMA address can have ambiguous matches when the same physical address maps multiple times, so best-fit logic may still avoid reporting in ambiguous cases. Cacheline overlap tracking can warn on legitimate advanced use unless attributes mark the mapping clean or skip CPU sync.

## Test Signals
Trigger double unmap, wrong unmap size/type/direction, missing `dma_mapping_error()`, stack/vmalloc/text/rodata mapping, SG segment too large or crossing boundary, sync outside allocation, unbind with leaked mappings, driver filter debugfs writes, dynamic pool growth, and cacheline overlap warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/debug.h -->
# sources/distributed-fs/ceph-client/kernel/dma/debug.h

## Purpose
This header declares the DMA API debug hooks and supplies no-op inline versions when DMA API debugging is disabled. It lets DMA mapping code call debug instrumentation unconditionally while compiling away the calls in normal builds.

## Important APIs, Types, And Functions
When `CONFIG_DMA_API_DEBUG` is set, it declares hooks for physical mapping/unmapping, scatterlist mapping/unmapping, coherent allocation/free, single and SG sync for CPU/device, and noncoherent page allocation/free. When disabled, the same names are static inline empty functions.

## Control Flow
There is no runtime control flow beyond compile-time selection. The enabled declarations resolve to `debug.c`; the disabled branch lets callers compile without code generation for debug checks.

## State, Persistence, And Dependencies
The header holds no state. It depends on core DMA types such as `struct device`, `struct scatterlist`, `struct page`, `phys_addr_t`, and `dma_addr_t` being visible through included DMA mapping headers in callers.

## Integration Points
DMA mapping implementation files include this header to instrument operations. It is the narrow interface between production DMA paths and the optional debug tracker.

## Risks
Prototype drift between this header and `debug.c` would break debug builds while non-debug builds still compile. Missing a hook in callers means a class of DMA misuse is invisible to `CONFIG_DMA_API_DEBUG`.

## Test Signals
Build both `CONFIG_DMA_API_DEBUG=y` and `n`, verify no undefined symbols in debug builds, and confirm non-debug builds do not create DMA debugfs files or instrumentation overhead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/direct.c -->
# sources/distributed-fs/ceph-client/kernel/dma/direct.c

## Purpose
This file implements the generic direct DMA mapping backend for systems that can translate CPU physical addresses directly to device DMA addresses, with fallbacks for SWIOTLB bounce buffering, CMA, coherent atomic pools, non-coherent remapping, encryption/decryption, and PCI P2PDMA.

## Important APIs, Types, And Functions
Important APIs include `dma_direct_get_required_mask()`, `dma_coherent_ok()`, `dma_direct_alloc()`, `dma_direct_free()`, `dma_direct_alloc_pages()`, `dma_direct_free_pages()`, `dma_direct_map_sg()`, `dma_direct_unmap_sg()`, sync helpers, `dma_direct_get_sgtable()`, `dma_direct_can_mmap()`, `dma_direct_mmap()`, `dma_direct_supported()`, `dma_direct_all_ram_mapped()`, `dma_direct_max_mapping_size()`, `dma_direct_need_sync()`, and `dma_direct_set_offset()`. Helpers choose GFP zones, allocate pages, use SWIOTLB, and encrypt/decrypt memory for confidential-computing shared DMA.

## Control Flow
Allocation aligns size, handles `DMA_ATTR_NO_KERNEL_MAPPING`, delegates to arch allocation for non-coherent devices when configured, tries global coherent pools, decides whether to remap or mark memory uncached, uses atomic pools when blocking is not allowed, then allocates pages from SWIOTLB/CMA/buddy and prepares them for coherent DMA. Free reverses those choices, including pool release, vunmap, clearing uncached mappings, re-encryption, and freeing pages. SG mapping handles PCI P2PDMA bus-address cases, direct physical mappings, SWIOTLB fallback, and unwind on failure. Mmap first tries per-device/global coherent pools, then remaps PFNs. Range-map helpers validate whether all RAM is covered by a device DMA range map.

## State, Persistence, And Dependencies
Global state is `zone_dma_limit` and optional device `dma_range_map` allocated by `dma_direct_set_offset()`. Most behavior is derived from `struct device` masks, coherence, bus limits, ranges, SWIOTLB state, and attributes. Dependencies include CMA, SWIOTLB, DMA pools, arch cache sync hooks, memory encryption helpers, vmalloc/remap APIs, scatterlists, PCI P2PDMA, and system RAM walking.

## Integration Points
The generic DMA ops layer calls these routines for direct mapping. `direct.h` exposes inline single-map/unmap/sync helpers. `coherent.c` and `contiguous.c` provide pool/CMA services used here. SWIOTLB and arch hooks provide bounce and cache maintenance behavior.

## Risks
Mask and bus-limit checks are security- and data-integrity-critical. Non-coherent cache sync ordering must match map/unmap direction. Error paths can intentionally leak pages if memory cannot be re-encrypted. `DMA_ATTR_NO_KERNEL_MAPPING` returns a page cookie rather than a CPU pointer. P2PDMA cases must not be bounced or translated incorrectly.

## Test Signals
Test coherent and non-coherent allocation/free, atomic pool allocation, SWIOTLB forced bounce, DMA mask overflow warnings, CMA fallback, highmem remap, encryption/decryption paths, `NO_KERNEL_MAPPING`, SG mapping unwind, PCI P2PDMA modes, mmap bounds, range-map coverage, and `dma_direct_need_sync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/direct.h -->
# sources/distributed-fs/ceph-client/kernel/dma/direct.h

## Purpose
This private header exposes the direct DMA backend interface and provides inline fast paths for single physical mappings, unmaps, and cache synchronization. It centralizes SWIOTLB, DMA attribute, device-capability, and non-coherent cache maintenance decisions used by the generic mapping layer.

## Important APIs, Types, And Functions
Declarations cover SG table creation, mmap support, sync need checks, SG map/unmap/sync, range coverage, and max mapping size. Inline functions include `dma_direct_sync_single_for_device()`, `dma_direct_sync_single_for_cpu()`, `dma_direct_map_phys()`, and `dma_direct_unmap_phys()`.

## Control Flow
`dma_direct_map_phys()` chooses between forced SWIOTLB bounce, rejecting incompatible `DMA_ATTR_CC_SHARED`, direct MMIO addresses, unencrypted translation, normal `phys_to_dma()`, or SWIOTLB fallback when the device cannot address the range or kmalloc bounce is needed. It performs device sync for non-coherent mappings unless skipped. `dma_direct_unmap_phys()` skips MMIO/required-coherent cases, syncs back for CPU unless requested otherwise, then asks SWIOTLB to unmap. Sync helpers translate DMA address to physical and call SWIOTLB and architecture cache hooks in the proper direction.

## State, Persistence, And Dependencies
The header holds no independent state. It depends on `linux/dma-direct.h`, `linux/memremap.h`, SWIOTLB APIs, device coherence and masks, DMA attributes, and architecture sync hooks.

## Integration Points
`direct.c` implements the declared non-inline functions. Generic DMA map ops and wrappers can use the inline helpers for low-overhead direct single mapping.

## Risks
Attribute combinations are subtle: MMIO, required coherent, skip CPU sync, and confidential-computing shared mappings change whether SWIOTLB or direct translation is legal. Incorrect flush argument use can miss cache maintenance. Overflow warning uses device mask and bus limit and must not dereference an unset mask in invalid device setup.

## Test Signals
Test direct map/unmap with coherent and non-coherent devices, `DMA_ATTR_SKIP_CPU_SYNC`, forced SWIOTLB, `DMA_ATTR_MMIO`, `DMA_ATTR_REQUIRE_COHERENT`, `DMA_ATTR_CC_SHARED`, kmalloc bounce thresholds, and cache sync calls in both directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/dummy.c -->
# sources/distributed-fs/ceph-client/kernel/dma/dummy.c

## Purpose
This file defines a fail-closed DMA ops table for devices or architectures that expose `struct dma_map_ops` but cannot perform DMA mappings. Every mapping capability fails, and unexpected unmap calls warn.

## Important APIs, Types, And Functions
`dma_dummy_mmap()` returns `-ENXIO`. `dma_dummy_map_phys()` returns `DMA_MAPPING_ERROR`. `dma_dummy_unmap_phys()` warns. `dma_dummy_map_sg()` returns `-EINVAL`. `dma_dummy_unmap_sg()` warns. `dma_dummy_supported()` returns false. `dma_dummy_ops` publishes these callbacks.

## Control Flow
Callers attempting mmap, physical mapping, SG mapping, or mask support get immediate failure. Unmap functions should be unreachable because corresponding map operations cannot succeed; they emit `WARN_ON_ONCE(true)` to flag misuse.

## State, Persistence, And Dependencies
There is no state. Dependencies are limited to DMA map ops types, scatterlists, VMAs, and warning support.

## Integration Points
Built when `CONFIG_ARCH_HAS_DMA_OPS` is enabled, this ops table can be assigned to devices that should not DMA or as a safe default before real ops are installed.

## Risks
Assigning dummy ops to a device that requires DMA causes all DMA setup to fail. Conversely, the fail-closed behavior is useful because it prevents accidental physical mappings on unsupported hardware. Unexpected unmap warnings indicate caller accounting bugs.

## Test Signals
Test that map calls return failure, DMA mask support reports false, mmap returns `-ENXIO`, and unmap callbacks warn only if a caller incorrectly unmaps a never-mapped buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/map_benchmark.c -->
# sources/distributed-fs/ceph-client/kernel/dma/map_benchmark.c

## Purpose
This file implements a debugfs-driven benchmark driver for DMA map/unmap latency. It can bind to a platform or PCI device, expose `/sys/kernel/debug/dma_map_benchmark`, and run kthreads that repeatedly map and unmap either a single contiguous buffer or a scatterlist.

## Important APIs, Types, And Functions
`struct map_benchmark_data` stores user parameters, target device, debugfs entry, direction, atomic timing sums, squared sums, and loop count. `struct map_benchmark_ops` abstracts benchmark modes. Single-buffer helpers allocate pages with `alloc_pages_exact()` and use `dma_map_single()`/`dma_unmap_single()`. SG helpers allocate one page per SG entry and use `dma_map_sg()`/`dma_unmap_sg()`. `map_benchmark_thread()` measures loop latencies. `do_map_benchmark()` creates/stops workers and computes averages/stddev. `map_benchmark_ioctl()` validates user input and runs `DMA_MAP_BENCHMARK`.

## Control Flow
Probe allocates per-device state and creates the debugfs file. The ioctl copies `struct map_benchmark` from userspace, validates mode, thread count, duration, transmit delay, NUMA node, granule, and direction, temporarily sets the device DMA mask, runs the benchmark, restores the old mask, then copies results back. Each worker prepares its buffers, optionally stains CPU caches for TO_DEVICE/BIDIRECTIONAL, times map and unmap separately in 100 ns units, waits the requested fake transfer delay, accumulates sums atomically, and yields with `cond_resched()`.

## State, Persistence, And Dependencies
State is per-bound-device devm memory and a debugfs dentry, plus per-run kthreads and buffers. The benchmark temporarily mutates `dev->dma_mask` through `dma_set_mask()` and restores it afterward. Dependencies include debugfs, DMA mapping API, kthreads, timekeeping, NUMA CPU masks, PCI and platform driver registration, and the UAPI in `uapi/linux/map_benchmark.h`.

## Integration Points
Userspace selftests can bind the benchmark driver to a device and issue the ioctl through debugfs. The file registers both PCI and platform drivers named `dma_map_benchmark`.

## Risks
Benchmarking changes the device DMA mask during the run; failure to restore would affect the real driver, so restoration is a key invariant. High thread counts and long durations can load the system. SG preparation must unwind partially allocated pages correctly. The file allows only one debugfs file name globally, so a second bound device fails as intended.

## Test Signals
Run the DMA map benchmark selftest in single and SG modes, all supported directions, different granules, NUMA binding, invalid parameter rejection, DMA mask restore after failure and success, map failure handling, module init/exit, and cleanup of debugfs on driver detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/map_benchmark.c -->
