# subset-b-000755 Research

Grouped research for OpenRISC architecture headers, kernel, library, and memory-management files plus the PA-RISC top-level build configuration files listed in subset `subset-b-000755`. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h

## Purpose
Defines the OpenRISC kernel serial baud base for early 8250 console code. The generic header assumes a fixed UART input clock, while OpenRISC derives it from the current CPU clock so early console output is timed correctly.

## Important APIs, Types, And Functions
The only exported interface is `BASE_BAUD`, computed as `cpuinfo_or1k[smp_processor_id()].clock_frequency / 16`. It includes `asm/cpuinfo.h` and is visible only under `__KERNEL__`.

## Control Flow
There is no function flow. Consumers expand the macro during serial setup, after CPU clock frequency has been populated from device tree setup.

## State And Persistence
No state is stored here. It depends on the per-CPU `cpuinfo_or1k` array, so baud behavior changes with the recorded CPU clock.

## Dependencies And Integration Points
Integrates with early 8250 serial console and OpenRISC CPU discovery. It assumes `smp_processor_id()` is valid for the calling context.

## Risks
If `clock_frequency` is unset or wrong, early console output uses the wrong divisor. SMP users must not evaluate the macro before per-CPU CPU info is initialized.

## Test Signals
Boot logs on 8250 early console at the expected baud rate; device-tree CPU `clock-frequency` changes should produce matching serial divisor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h

## Purpose
Declares the architecture setup hook used to process the boot-time device tree before the generic kernel setup path needs platform data.

## Important APIs, Types, And Functions
Exports `void __init or1k_early_setup(void *fdt);` for C code and includes `asm-generic/setup.h`. The declaration is hidden from assembly.

## Control Flow
`head.S` calls `or1k_early_setup()` after enabling the MMU and validating the FDT magic. The implementation selects the passed FDT or the built-in DTB and calls early device-tree scanning.

## State And Persistence
The header stores no state. It introduces the function that seeds global OF/FDT and memblock reservation state.

## Dependencies And Integration Points
Depends on Linux init annotations and the generic setup interface. It links the assembly boot path with `kernel/setup.c`.

## Risks
The signature is part of the assembly/C boot contract. Changing it without updating `head.S` breaks early boot.

## Test Signals
OpenRISC boot with external and built-in DTBs should report the selected FDT and reach `setup_arch()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h

## Purpose
Provides the OpenRISC SMP interface for CPU identity, CPU discovery, IPI dispatch, and architecture call-function hooks.

## Important APIs, Types, And Functions
`raw_smp_processor_id()` reads `current_thread_info()->cpu`, while `hard_smp_processor_id()` reads `SPR_COREID`. It declares `smp_init_cpus()`, call-function IPI senders, `set_smp_cross_call()`, and `handle_IPI()`.

## Control Flow
Generic SMP code calls these hooks to enumerate CPUs and deliver reschedule or call-function IPIs. The implementation in `kernel/smp.c` wires a platform IPI sender and uses `SPR_COREID` during boot.

## State And Persistence
The header itself has no state. Its declarations operate on CPU masks, per-CPU thread info, and the hardware core ID SPR.

## Dependencies And Integration Points
Depends on `asm/spr.h` and `asm/spr_defs.h`. Integrates Linux SMP core, device-tree CPU nodes, interrupt controller IPI plumbing, and OpenRISC TLB shootdown.

## Risks
Wrong CPU IDs corrupt per-CPU state and TLB shootdown targeting. `set_smp_cross_call()` must be installed before secondary CPU startup.

## Test Signals
SMP boot should mark all DT CPUs possible/present, bring secondaries online, and successfully run `smp_call_function*()` and reschedule IPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h

## Purpose
Defines inline assembly accessors for OpenRISC special-purpose registers.

## Important APIs, Types, And Functions
`mtspr(_spr, _val)` writes an immediate SPR address, `mtspr_off(_spr, _off, _val)` writes indexed SPRs, `mfspr(add)` reads an SPR, and `mfspr_off(add, offset)` reads an indexed SPR.

## Control Flow
There is no higher-level flow; callers issue `l.mtspr` or `l.mfspr` directly. These helpers underpin timer, MMU, cache, interrupt, CPU-info, and SMP code.

## State And Persistence
Writes change hardware CPU state such as SR, TTMR, TLB, cache-control, PIC, and PM registers. Effects persist until overwritten or reset.

## Dependencies And Integration Points
SPR numeric constants come from `spr_defs.h`. Inline constraints use OpenRISC assembler support for the `K` immediate operand.

## Risks
Invalid SPR numbers or ordering mistakes can corrupt privileged CPU state. These helpers do not provide memory barriers beyond volatile asm.

## Test Signals
Boot-time reads of `SPR_UPR`, `SPR_VR`, `SPR_TTCR`, and TLB/cache SPR writes should behave consistently on simulator and hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h

## Purpose
Defines the OpenRISC SPR address map and bit masks for system, MMU, cache, debug, performance, power, PIC, tick timer, FPU, and simulator NOP facilities.

## Important APIs, Types, And Functions
Major address groups include `SPRGROUP_SYS`, `DMMU`, `IMMU`, `DC`, `IC`, `D`, `PC`, `PM`, `PIC`, `TT`, and `FP`. Important registers include `SPR_SR`, `SPR_EVBAR`, exception PC/address/status bases, TLB match/translate ranges, cache block invalidate/flush registers, `SPR_COREID`, `SPR_NUMCORES`, `SPR_TTMR`, `SPR_TTCR`, and `SPR_FPCSR`.

## Control Flow
The file has no executable flow. It supplies constants that are consumed by boot assembly, exception return, TLB miss handlers, timer setup, cache maintenance, FPU exception handling, and SMP CPU identification.

## State And Persistence
Definitions describe privileged hardware state. SR bits control MMU, cache, interrupt, supervisor, delay-slot, and endian modes; TLB and cache SPRs affect translations and coherency; tick timer bits control clocksource and clockevent behavior.

## Dependencies And Integration Points
Paired with `spr.h` accessors. The numeric values must match the OpenRISC 1000 architecture and the assembly code in `head.S` and `entry.S`.

## Risks
Mask or offset drift is high impact: a wrong SR, TLB, cache, or TTMR bit can break boot, memory protection, interrupt delivery, or timing. Some comments reflect old simulator heritage, so changes require architecture-manual validation.

## Test Signals
Cross-build all OpenRISC configs; boot through MMU enable; verify CPU feature printout, cacheinfo, timer interrupts, FPU signal codes, TLB miss refill, and SMP core ID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h

## Purpose
Advertises OpenRISC architecture implementations of `memset()` and `memcpy()` to generic kernel string code.

## Important APIs, Types, And Functions
Defines `__HAVE_ARCH_MEMSET` and `__HAVE_ARCH_MEMCPY`, then declares `memset(void *s, int c, __kernel_size_t n)` and `memcpy(void *dest, const void *src, __kernel_size_t n)`.

## Control Flow
No flow in the header. Build selection routes calls to `arch/openrisc/lib/memset.S` and `memcpy.c`.

## State And Persistence
No persistent state. The functions mutate caller-provided memory.

## Dependencies And Integration Points
Requires kernel type definitions for `__kernel_size_t`. Integrated by generic string headers and module exports.

## Risks
Prototype mismatch would break builtins, modules, or sanitizer expectations. The implementations do not provide overlap semantics for `memcpy`.

## Test Signals
Kernel string selftests, boot-time memory initialization, and module references to exported `memset`/`memcpy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h

## Purpose
Implements the generic syscall-inspection API for OpenRISC `pt_regs`.

## Important APIs, Types, And Functions
`syscall_get_nr()` and `syscall_set_nr()` use `orig_gpr11`; rollback restores `gpr[11]`. Return/error accessors treat `gpr[11]` as the return register. Argument helpers copy six arguments from `gpr[3]` through `gpr[8]`. `syscall_get_arch()` returns `AUDIT_ARCH_OPENRISC`.

## Control Flow
Generic tracing, audit, seccomp, and restart paths call these small inlines while `entry.S` owns the low-level syscall dispatch.

## State And Persistence
Only modifies the live saved register frame. `orig_gpr11` is persistent across a syscall return path for restart and tracing decisions.

## Dependencies And Integration Points
Depends on `pt_regs` layout, audit constants, `IS_ERR_VALUE()`, and string copying. Integrates with `ptrace.c`, `signal.c`, and syscall entry assembly.

## Risks
Any register convention mismatch breaks syscall restart, tracing, audit arguments, or return values. Argument copy count must stay aligned with the OpenRISC syscall ABI.

## Test Signals
Run ptrace/audit/seccomp syscall tests, syscall restart after signals, and six-argument syscall cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h

## Purpose
Declares OpenRISC syscall wrappers that differ from generic syscall prototypes.

## Important APIs, Types, And Functions
Declares `sys_or1k_atomic()`, includes generic syscall declarations, and declares assembly wrappers `__sys_clone()`, `__sys_clone3()`, and `__sys_fork()`.

## Control Flow
`sys_call_table.c` aliases generic syscall names to these wrappers. `entry.S` wrappers save extra callee-saved registers before calling the common clone/fork implementations.

## State And Persistence
No state in the header. The wrappers preserve user register state across fork-like paths.

## Dependencies And Integration Points
Depends on OpenRISC syscall ABI, generic syscall prototypes, `clone_args`, and user pointer annotations.

## Risks
Wrapper signature drift causes stack/register corruption at syscall boundaries. `sys_or1k_atomic()` is legacy and must preserve ABI even if internally minimal.

## Test Signals
Fork/clone/clone3 syscall tests, module build checks, and atomic syscall compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h

## Purpose
Declares the architecture API for writing a single OpenRISC instruction into kernel text or vmalloc text.

## Important APIs, Types, And Functions
`int patch_insn_write(void *addr, u32 insn);` writes a 4-byte instruction and returns an error code.

## Control Flow
Runtime patching users such as jump labels call this API after computing the replacement instruction. The implementation serializes patching and invalidates I-cache over the patched word.

## State And Persistence
No header state. The implementation mutates executable kernel memory until it is patched again or rebooted.

## Dependencies And Integration Points
Depends on Linux integer types and `kernel/patching.c`. Used by `kernel/jump_label.c`.

## Risks
Callers must pass aligned instruction addresses and fully encoded OpenRISC instructions. Incorrect patching can crash all CPUs.

## Test Signals
Jump-label toggling under `CONFIG_JUMP_LABEL`, alignment-error tests, and instruction-cache coherency after patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h

## Purpose
Defines OpenRISC low-level thread metadata, stack sizing, thread flags, and current-thread access used by entry assembly and scheduler code.

## Important APIs, Types, And Functions
`THREAD_SIZE_ORDER` is zero and `THREAD_SIZE` is `PAGE_SIZE`. `struct thread_info` holds `task`, `flags`, `cpu`, `preempt_count`, and `ksp`. It declares `current_thread_info_set[NR_CPUS]` and maps thread flags such as `_TIF_SYSCALL_TRACE`, `_TIF_NOTIFY_RESUME`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, and `_TIF_NOTIFY_SIGNAL`.

## Control Flow
Entry code loads current thread info from `current_thread_info_set`, checks `_TIF_WORK_MASK` before returning to userspace, and uses `ksp` for exception and context-switch stack handling.

## State And Persistence
Per-task `thread_info` persists for task lifetime. `ksp` records the saved kernel stack frame across context switches; `flags` drives syscall tracing, signal delivery, and rescheduling.

## Dependencies And Integration Points
Requires `processor.h`, task layout, and generated asm offsets. Integrated by `entry.S`, `head.S`, `process.c`, `smp.c`, and generic scheduler code.

## Risks
Layout changes must update `asm-offsets.c` consumers. Wrong `THREAD_SIZE` or flag masks break exception entry, stack switching, and userspace return work.

## Test Signals
Context-switch stress, signal delivery, preemption/reschedule tests, SMP boot, and generated asm offset consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h

## Purpose
Declares OpenRISC timer and SMP cycle-counter synchronization hooks.

## Important APIs, Types, And Functions
Exports `openrisc_clockevent_init()`, `openrisc_timer_set()`, `openrisc_timer_set_next()`, and, under SMP, `synchronise_count_master()` and `synchronise_count_slave()`.

## Control Flow
`time_init()` and secondary CPU startup call clockevent initialization; timer interrupt setup calls the set-next-event path; SMP bring-up synchronizes TTCR counters.

## State And Persistence
The functions manipulate per-CPU tick timer SPRs and per-CPU clockevent state.

## Dependencies And Integration Points
Implemented by `kernel/time.c` and `kernel/sync-timer.c`. Integrated with clocksource, clockevents, IRQ, and SMP boot.

## Risks
Timer APIs assume the OpenRISC tick timer exists and has a 28-bit compare period. Wrong ordering can miss clock events or desynchronize SMP sched clocks.

## Test Signals
Boot without timer should panic; normal boot should register clocksource/clockevent, deliver periodic scheduler ticks, and sync CPU counters during SMP startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h

## Purpose
Provides OpenRISC cycle-counter access for generic timekeeping and delay loops.

## Important APIs, Types, And Functions
Defines `get_cycles()` to read `SPR_TTCR` through `mfspr()`. Sets `CLOCK_TICK_RATE` to `1000` as a legacy value and declares `ARCH_HAS_READ_CURRENT_TIMER`.

## Control Flow
Delay and clocksource code call `get_cycles()` repeatedly. No control flow is implemented here beyond the inline SPR read.

## State And Persistence
Reads the hardware tick timer counter; it does not mutate state.

## Dependencies And Integration Points
Depends on `asm-generic/timex.h`, `spr.h`, and `spr_defs.h`. Used by `lib/delay.c` and `kernel/time.c`.

## Risks
If TTCR is stopped or absent, delays and clocksource reads are invalid. Wraparound is 32-bit and callers must use delta arithmetic.

## Test Signals
Delay calibration, monotonic clocksource reads across wraps, and `read_current_timer()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h

## Purpose
Adapts generic Linux TLB gather code for OpenRISC.

## Important APIs, Types, And Functions
Includes `linux/pagemap.h` and `asm-generic/tlb.h`. The comment records that OpenRISC lacks an efficient `flush_tlb_range()`, so broad mm flushes are preferred in generic gathering.

## Control Flow
No local code. Generic mmu_gather paths use this header when freeing page tables and unmapping memory.

## State And Persistence
No state. TLB state is controlled by `tlbflush.h` and `mm/tlb.c`.

## Dependencies And Integration Points
Integrates OpenRISC with generic memory-management page-table teardown.

## Risks
Performance risk from broad flushes. Correctness depends on the OpenRISC flush implementations invalidating both data and instruction TLB entries.

## Test Signals
Page unmap/remap tests, mmap/munmap stress, and TLB shootdown behavior under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h

## Purpose
Declares local and SMP-aware TLB invalidation APIs for OpenRISC.

## Important APIs, Types, And Functions
Local functions include `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_page()`, and `local_flush_tlb_range()`. Non-SMP maps generic names directly to local versions; SMP declares global versions implemented in `smp.c`. `flush_tlb()` flushes `current->mm`, and `flush_tlb_kernel_range()` routes through range flushing.

## Control Flow
Memory-management updates call these hooks after page table changes. SMP builds target remote CPUs through IPI helpers in `kernel/smp.c`.

## State And Persistence
Invalidates hardware DTLB and ITLB entries. No software state is stored here.

## Dependencies And Integration Points
Depends on `mm_struct`, `vm_area_struct`, current task state, and OpenRISC processor definitions. Used by page faults, DMA cache-inhibit changes, fixmap setup, and generic mm.

## Risks
`flush_tlb()` assumes `current->mm` is non-null. Kernel range flushing with `vma == NULL` must be handled by the implementation, especially on SMP.

## Test Signals
TLB invalidation after mprotect, munmap, vmalloc, module loading, DMA uncached mapping, and SMP shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h

## Purpose
Implements OpenRISC user-memory access primitives with exception-table fixups.

## Important APIs, Types, And Functions
Provides `get_user`, `put_user`, unchecked variants, size dispatch for 1/2/4/8 byte accesses, inline assembly load/store fixup blocks, `raw_copy_from_user()`, `raw_copy_to_user()`, `clear_user()`, `strncpy_from_user()`, and `strnlen_user()`.

## Control Flow
Checked forms call `access_ok()` first, then size-specific inline assembly emits faulting access labels and fixup labels. If a fault happens, the exception table redirects to code setting `-EFAULT` and zeroing destination for reads. Bulk copy and clear call assembly routines in `lib/string.S`.

## State And Persistence
Mutates user or kernel buffers. Fault state is not persisted, but return values report bytes not copied or `-EFAULT`.

## Dependencies And Integration Points
Depends on `asm/extable.h`, generic `access_ok`, OpenRISC instructions, and exception handling in `mm/fault.c`. Used by signals, ptrace, syscall argument/result paths, and drivers.

## Risks
Inline asm constraints and exception-table entries are correctness-critical. 64-bit accesses split into two 32-bit operations, so partial fault behavior must be acceptable to callers. Unchecked variants require prior validation.

## Test Signals
Usercopy selftests, signal-frame copy faults, ptrace regset copy faults, bad user pointer handling, and KASAN/usercopy hardening builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h

## Purpose
Selects syscall families wanted by the OpenRISC kernel side and includes the UAPI syscall number header.

## Important APIs, Types, And Functions
Defines `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_CLONE`, and `__ARCH_WANT_TIME32_SYSCALLS`, then includes `uapi/asm/unistd.h`.

## Control Flow
No control flow. The defines influence generated syscall tables and generic syscall declarations.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated with syscall table generation, `sys_call_table.c`, `entry.S`, and generic unistd generation.

## Risks
Changing these wants alters userspace ABI availability. Time32 and legacy fork/clone choices must remain compatible with OpenRISC userlands.

## Test Signals
Generated `unistd_32.h` consistency, syscall table build, and userspace ABI tests for legacy syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h

## Purpose
Declares the OpenRISC stack unwinding callback API.

## Important APIs, Types, And Functions
`unwind_stack(void *data, unsigned long *stack, void (*trace)(void *data, unsigned long addr, int reliable))` scans a kernel stack and reports return addresses with a reliability flag.

## Control Flow
Callers supply a starting stack pointer and callback. `kernel/unwinder.c` either validates frame-pointer records or scans for text addresses.

## State And Persistence
No state. It observes stack memory and text addresses.

## Dependencies And Integration Points
Used by `traps.c` for crash output and `stacktrace.c` for stack trace collection.

## Risks
Reliability depends on frame pointers. Non-frame-pointer mode can produce false positives and marks entries unreliable.

## Test Signals
Stacktrace selftests with `CONFIG_FRAME_POINTER`, crash dump output, and scheduler-stack filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/vmalloc.h

## Purpose
Provides the OpenRISC architecture vmalloc override header, currently empty.

## Important APIs, Types, And Functions
No APIs are defined; the include guard prevents accidental multiple inclusion.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Allows generic vmalloc code to include an architecture header without OpenRISC-specific overrides.

## Risks
Future vmalloc constraints may be missed if this remains empty while architecture requirements change.

## Test Signals
Generic vmalloc, module allocation, ioremap, and text patching with vmalloc-backed memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild

## Purpose
Controls exported UAPI header generation for OpenRISC.

## Important APIs, Types, And Functions
Adds `unistd_32.h` to syscall-generated headers and selects generic `ucontext.h`.

## Control Flow
Kbuild consumes this declarative file during `headers_install` and syscall header generation.

## State And Persistence
No runtime state. It affects generated header artifacts.

## Dependencies And Integration Points
Integrates OpenRISC UAPI with generic syscall and ucontext header generation.

## Risks
Omitting generated syscall headers breaks userspace builds; replacing generic `ucontext.h` would affect signal ABI expectations.

## Test Signals
`make headers_install` for OpenRISC and libc builds using generated unistd/ucontext headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h

## Purpose
Declares OpenRISC userspace byte order as big endian.

## Important APIs, Types, And Functions
Includes `linux/byteorder/big_endian.h`.

## Control Flow
No control flow; it is a compile-time UAPI selection.

## State And Persistence
No state.

## Dependencies And Integration Points
Consumed by exported headers and userspace code compiling against OpenRISC ABI.

## Risks
This is an ABI statement. Changing it would break structure layout, ELF data expectations, networking conversions, and userspace compatibility.

## Test Signals
Headers-install builds and userspace endian macro checks for OpenRISC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h

## Purpose
Defines OpenRISC ELF ABI constants, relocation numbers, register-set types, and core-dump metadata shared with userspace.

## Important APIs, Types, And Functions
Defines `R_OR1K_*` relocation constants, old `R_OR32_*` aliases, `elf_greg_t`, `ELF_NGREG`, `elf_gregset_t`, `elf_fpregset_t`, `EM_OR32`, `ELF_ARCH`, `ELF_CLASS`, and `ELF_DATA`.

## Control Flow
No executable flow. Module relocation, binutils, loaders, core dumps, ptrace users, and debuggers consume these constants.

## State And Persistence
Defines ABI layouts for persisted ELF files and core dumps.

## Dependencies And Integration Points
Includes `asm/ptrace.h` for `struct user_regs_struct` and FPU state. `kernel/module.c` implements a subset of relocations from this list.

## Risks
Relocation numbering and ELF metadata are stable ABI. Mismatches with toolchain definitions break module loading, dynamic linking, debugging, and core analysis.

## Test Signals
OpenRISC toolchain relocation tests, module relocation tests, core dump register inspection, and ELF header validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h

## Purpose
Defines OpenRISC userspace execution page size and imports generic parameter constants.

## Important APIs, Types, And Functions
Sets `EXEC_PAGESIZE` to `8192` and includes `asm-generic/param.h`.

## Control Flow
No control flow.

## State And Persistence
No runtime state. The value is part of userspace-visible ABI expectations.

## Dependencies And Integration Points
Used by libc, proc tooling, and generic kernel UAPI parameters.

## Risks
Changing `EXEC_PAGESIZE` may break binary loaders and userspace assumptions about OpenRISC page granularity.

## Test Signals
Headers-install checks and userspace page-size/auxiliary-vector behavior on OpenRISC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h

## Purpose
Defines the userspace-visible OpenRISC ptrace register layout.

## Important APIs, Types, And Functions
`struct user_regs_struct` contains 32 GPRs plus `pc` and `sr`. `struct __or1k_fpu_state` contains `fpcsr`.

## Control Flow
No control flow. `kernel/ptrace.c`, core dumps, and debuggers serialize/deserialize these layouts.

## State And Persistence
Defines ptrace and core-dump state persisted across debugger reads and core files.

## Dependencies And Integration Points
Included by UAPI ELF and signal context headers. Must match `genregs_get()` and `genregs_set()` behavior.

## Risks
Any layout change is an ABI break. User writes to SR are intentionally constrained by kernel ptrace code.

## Test Signals
`PTRACE_GETREGSET`/`SETREGSET`, GDB register display, and core dump register-set tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h

## Purpose
Defines the user ABI signal machine context for OpenRISC.

## Important APIs, Types, And Functions
`struct sigcontext` embeds `struct user_regs_struct regs` first, followed by a union holding `fpcsr` or legacy `oldmask`.

## Control Flow
`kernel/signal.c` writes this structure when building an RT signal frame and restores it in `rt_sigreturn`.

## State And Persistence
The structure persists on the user stack while a signal handler runs and determines restored user register/FPU state.

## Dependencies And Integration Points
Includes `asm/ptrace.h`; paired with generic `ucontext` and OpenRISC signal frame setup.

## Risks
Field order is ABI-sensitive, especially `regs` being first. Bad restoration could let userspace set privileged SR bits, so kernel masks supervisor mode.

## Test Signals
Signal handler return tests, alternate signal stack tests, FPU status preservation, and libc `ucontext_t` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h

## Purpose
Exports the generated OpenRISC 32-bit syscall numbers to userspace.

## Important APIs, Types, And Functions
Includes `asm/unistd_32.h`.

## Control Flow
No control flow. Generated syscall constants are consumed by libc, assembly stubs, seccomp filters, and kernel syscall table generation.

## State And Persistence
No runtime state; syscall numbers are stable ABI.

## Dependencies And Integration Points
Generated through UAPI Kbuild. Kernel side includes this via `asm/unistd.h` and builds `sys_call_table`.

## Risks
Generation or include failure breaks all userspace syscall constants. Renumbering is not ABI-compatible.

## Test Signals
Headers install, libc build, syscall table size checks, and userspace syscall smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile

## Purpose
Selects OpenRISC kernel objects and linker script generation.

## Important APIs, Types, And Functions
Builds `vmlinux.lds` for builtin kernels. Core objects include `head.o`, `setup.o`, `or32_ksyms.o`, `process.o`, `dma.o`, `traps.o`, `time.o`, `irq.o`, `entry.o`, `ptrace.o`, `signal.o`, `sys_call_table.o`, `unwinder.o`, and `cacheinfo.o`. Optional objects include jump labels, SMP, stacktrace, modules, OF prom support, and always `patching.o`.

## Control Flow
Kbuild uses these assignments to compile boot, exception, process, syscall, and MMU support into the architecture kernel.

## State And Persistence
No runtime state; controls linked code availability.

## Dependencies And Integration Points
Must align with Kconfig options and references from assembly/C code.

## Risks
Omitting an object causes link failures or missing runtime hooks. Including feature objects without Kconfig dependencies can break minimal builds.

## Test Signals
Build matrix with `SMP`, `MODULES`, `STACKTRACE`, `JUMP_LABEL`, and `OF` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c

## Purpose
Generates C-accurate constants for assembly code to access task, thread, and register-frame fields.

## Important APIs, Types, And Functions
`main()` emits `DEFINE()` values for task fields, `thread_info` fields, `PT_SIZE`, `STACK_FRAME_OVERHEAD`, `INT_FRAME_SIZE`, and `NUM_USER_SEGMENTS`.

## Control Flow
Kbuild compiles this file to assembly and extracts generated definitions into `asm-offsets.h`, which is included by `entry.S` and `head.S`.

## State And Persistence
No runtime state. The generated constants persist as build artifacts.

## Dependencies And Integration Points
Depends on `task_struct`, `thread_info`, `pt_regs`, OpenRISC stack constants, and Linux kbuild offset extraction.

## Risks
Missing offsets cause assembly to save or restore wrong fields. Any layout change must be reflected here before assembly is safe.

## Test Signals
Successful OpenRISC build after structure changes and boot through exception entry/context switch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c

## Purpose
Populates Linux cacheinfo data from OpenRISC cache configuration SPRs.

## Important APIs, Types, And Functions
`init_cache_level()` detects D-cache and I-cache presence, reads `SPR_DCCFGR`/`SPR_ICCFGR`, derives ways, sets, line size, and total size, and sets per-CPU leaf counts. `populate_cache_leaves()` fills `struct cacheinfo` leaves and D-cache write policy.

## Control Flow
Generic cacheinfo initialization calls level discovery first, then leaf population. Missing UPR or no caches returns `-ENOENT`.

## State And Persistence
Stores derived cache descriptors in `cpuinfo_or1k` and Linux per-CPU cacheinfo structures. Hardware cache configuration is read-only here.

## Dependencies And Integration Points
Depends on `SPR_UPR`, cache configuration masks, `cpu_cache_is_present()`, and generic cacheinfo sysfs.

## Risks
Uses `smp_processor_id()` for CPU info while accepting a `cpu` argument; unusual call contexts could describe the wrong CPU. Wrong bit decoding misreports cache geometry.

## Test Signals
`/sys/devices/system/cpu/cpu*/cache` contents, boot logs for cache geometry, and SMP systems with per-CPU cache data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c

## Purpose
Implements OpenRISC DMA cache-coherency helpers for uncached kernel mappings and explicit cache maintenance.

## Important APIs, Types, And Functions
`arch_dma_set_uncached()` walks kernel page tables, sets `_PAGE_CI`, flushes TLB entries, and writes back D-cache lines. `arch_dma_clear_uncached()` clears `_PAGE_CI`. `arch_sync_dma_for_device()` flushes for `DMA_TO_DEVICE` and invalidates for `DMA_FROM_DEVICE`.

## Control Flow
The set/clear paths lock `init_mm`, use `walk_kernel_page_table_range()`, and call PTE callbacks. Sync paths switch on DMA direction.

## State And Persistence
Mutates kernel PTE cache-inhibit bits until cleared. Cache lines and TLB entries are transient hardware state.

## Dependencies And Integration Points
Depends on Linux DMA map ops, page table walkers, OpenRISC cacheflush and TLB APIs, and `_PAGE_CI`.

## Risks
Missing TLB flush leaves stale cacheable translations. `DMA_BIDIRECTIONAL` intentionally does no automatic maintenance, requiring caller-managed sync. Range alignment and page-table walk errors are important.

## Test Signals
DMA mapping tests with non-coherent devices, cache-inhibit PTE inspection, and data integrity for device read/write buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S

## Purpose
Contains OpenRISC runtime exception handlers, syscall dispatch, user return work handling, context switching, fork wrappers, signal-return trampoline entry, and the legacy atomic syscall.

## Important APIs, Types, And Functions
Key labels include `_bus_fault_handler`, `_data_page_fault_handler`, `_insn_page_fault_handler`, `_timer_handler`, `_external_irq_handler`, `_sys_call_handler`, `_ret_from_intr`, `_ret_from_exception`, `ret_from_fork`, `_switch`, `__sys_clone`, `__sys_clone3`, `__sys_fork`, `sys_rt_sigreturn`, and `sys_or1k_atomic`. Macros save/restore `pt_regs`, manage interrupt tracing, and clear `lwa_flag`.

## Control Flow
Exception stubs save register state then call C handlers in `traps.c`, `fault.c`, `time.c`, or generic IRQ code. Syscall entry saves ABI-required registers, enables interrupts, optionally traces, bounds-checks the syscall number, calls through `sys_call_table`, stores `r11`, handles syscall-exit tracing, checks `_TIF_WORK_MASK`, and either returns through a fast path or calls `do_work_pending()`. `_switch` saves callee-saved registers and swaps `thread_info->ksp`.

## State And Persistence
Persists task register frames on kernel stacks, updates `orig_gpr11`, changes EPCR/ESR for return, clears load/store-atomic emulation state, and changes current kernel stack pointer.

## Dependencies And Integration Points
Depends on generated asm offsets, `thread_info` flags, syscall table, C exception handlers, scheduler, signal handling, ptrace/audit, and SPR definitions.

## Risks
This is the highest-risk ABI and privilege boundary. Register save omissions break syscall restart, ptrace, fork, or context switch. Interrupt state around EPCR/ESR restore is critical. The atomic syscall disables interrupts and ignores its type argument, so compatibility relies on legacy expectations.

## Test Signals
Syscall ABI tests, ptrace/audit syscall tracing, signal restart tests, interrupt return tests, fork/clone stress, context-switch stress, and illegal/page/timer/IRQ exception coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S

## Purpose
Implements OpenRISC reset vectors, early boot, exception vector dispatch, boot-time and runtime TLB miss handlers, cache/MMU enabling, secondary CPU parking/startup, emergency UART output, and initial page-aligned data structures.

## Important APIs, Types, And Functions
Important labels include `_start`, `_dispatch_*` vector entries, `boot_dtlb_miss_handler`, `boot_itlb_miss_handler`, `dtlb_miss_handler`, `itlb_miss_handler`, `_ic_enable`, `_dc_enable`, `_flush_tlb`, `secondary_wait`, `secondary_start`, `_emergency_putc`, `_emergency_print`, `_emergency_print_nr`, `_early_uart_init`, `_secondary_evbar`, `swapper_pg_dir`, and `_unhandled_stack`.

## Control Flow
Reset jumps to `_start`, clears BSS/registers, starts TTCR, enables caches, flushes TLB, enables MMU, validates the FDT pointer, calls `or1k_early_setup()`, and enters `start_kernel()`. Vector slots use `EXCEPTION_HANDLE()` to build frames and jump into `entry.S` handlers. Boot TLB handlers identity-map early addresses; later handlers walk `current_pgd` and refill DTLB/ITLB or fall back to page-fault handlers.

## State And Persistence
Initializes SR, TTMR, cache state, TLB entries, `thread_info->ksp`, `swapper_pg_dir`, and secondary-release handshake state. Emergency output may use shadow GPRs or low memory scratch.

## Dependencies And Integration Points
Depends on linker placement, OpenRISC SPRs, generated offsets, FDT magic, serial configuration, page table layout, `current_pgd`, `current_thread_info_set`, and C setup/SMP entry points.

## Risks
Early code runs with changing address translation and must carefully convert virtual to physical addresses. Runtime TLB refill assumes two-level page tables and page-size/bit-mask contracts. Emergency UART constants are platform-specific.

## Test Signals
Boot on simulator and hardware, FDT fallback, MMU/caches enabled, runtime TLB misses resolved, secondary CPUs released, and early exception/emergency UART diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c

## Purpose
Provides OpenRISC interrupt flag save/restore helpers and initializes irqchip support.

## Important APIs, Types, And Functions
`arch_local_save_flags()` returns `SPR_SR_IEE | SPR_SR_TEE` bits from `SPR_SR`. `arch_local_irq_restore()` restores those bits while preserving other SR state. `init_IRQ()` calls `irqchip_init()`.

## Control Flow
Generic IRQ and locking code use save/restore helpers. Boot calls `init_IRQ()` during interrupt subsystem initialization.

## State And Persistence
Mutates SR interrupt-enable bits. No software state is stored.

## Dependencies And Integration Points
Depends on `mfspr/mtspr`, SPR bit definitions, irqchip framework, and exported irqflags API.

## Risks
Restore must not clobber MMU/cache/supervisor bits. Treating tick timer and external interrupt enables as a pair affects timer behavior.

## Test Signals
IRQ enable/disable tracing, timer interrupts, external irqchip probe, and lockdep/irqflags tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/jump_label.c

## Purpose
Implements OpenRISC static key jump-label transformation.

## Important APIs, Types, And Functions
`arch_jump_label_transform_queue()` computes either an `l.j` immediate or `OPENRISC_INSN_NOP` and writes it directly during early boot or via `patch_insn_write()` later. `arch_jump_label_transform_apply()` calls `kick_all_cpus_sync()`.

## Control Flow
Static key updates queue transformation entries, patch instruction words, and synchronize CPUs so stale instruction streams are not used.

## State And Persistence
Mutates kernel text at jump-label sites. No private persistent state.

## Dependencies And Integration Points
Depends on jump label core, instruction encodings, memory text patching, cache flushes, and CPU synchronization.

## Risks
The code writes only the immediate bits for jump form, relying on the original instruction opcode layout. Offset range must fit signed 26-bit branch displacement. Incorrect cache sync can execute stale code.

## Test Signals
`CONFIG_JUMP_LABEL` boot, static key toggling, branch range warnings, and tracepoint/static-branch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c

## Purpose
Applies OpenRISC ELF RELA relocations while loading kernel modules.

## Important APIs, Types, And Functions
`apply_relocate_add()` handles `R_OR1K_32`, `LO_16_IN_INSN`, `HI_16_IN_INSN`, `INSN_REL_26`, `32_PCREL`, `AHI16`, and `SLO16` relocations.

## Control Flow
For each relocation, the loader finds the target location, resolves symbol value plus addend, rewrites the instruction/data word or halfword, and logs unknown relocation types.

## State And Persistence
Mutates module text/data sections before module execution. No global state.

## Dependencies And Integration Points
Depends on UAPI ELF relocation constants, module loader section layout, OpenRISC instruction encoding, and module symbol resolution.

## Risks
Unknown relocations only log an error and still return success, which can leave a broken module loaded. Halfword writes are endian/layout-sensitive. Branch relocation range is not explicitly checked.

## Test Signals
Load modules using each supported relocation type; verify unknown relocations fail expectations; run module text execution and symbol reference tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c

## Purpose
Exports OpenRISC compiler helper routines and architecture usercopy/string helpers to modules.

## Important APIs, Types, And Functions
Exports libgcc-style helpers `__udivsi3`, `__divsi3`, `__umodsi3`, `__modsi3`, `__muldi3`, `__ashrdi3`, `__ashldi3`, `__lshrdi3`, `__ucmpdi2`, plus `__copy_tofrom_user`, `__clear_user`, and `memset`.

## Control Flow
No runtime control flow beyond export declarations.

## State And Persistence
No state.

## Dependencies And Integration Points
Supports modules compiled with helper calls not inlined by the compiler and modules needing exported usercopy/string routines.

## Risks
Missing exports cause module link/load failures. Exporting low-level helpers expands module ABI surface.

## Test Signals
External module builds using division, 64-bit arithmetic, memset, and usercopy helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/or32_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c

## Purpose
Implements safe single-instruction runtime patching for OpenRISC kernel text.

## Important APIs, Types, And Functions
`patch_map()` maps core text through `__pa_symbol()` or vmalloc text through `vmalloc_to_page()` into a fixmap slot. `__patch_insn_write()` serializes with `patch_lock`, writes via `copy_to_kernel_nofault()`, invalidates I-cache, and clears the fixmap. `patch_insn_write()` validates 4-byte alignment.

## Control Flow
Callers request an instruction write. The implementation maps the physical page writable through `FIX_TEXT_POKE0`, writes one 4-byte instruction, invalidates local I-cache over that word, unmaps, and unlocks.

## State And Persistence
Mutates executable memory and transient fixmap PTEs. Uses a global raw spinlock.

## Dependencies And Integration Points
Depends on fixmap, section classification, vmalloc pages, I-cache maintenance, and `text-patching.h`. Used by jump labels.

## Risks
Only local I-cache invalidation occurs here; callers needing cross-CPU sync must arrange it. Unaligned addresses fail. Incorrect page classification or fixmap use can corrupt unrelated text.

## Test Signals
Jump-label patching after boot, vmalloc/module text patching, alignment failure tests, and SMP instruction visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/patching.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c

## Purpose
Implements OpenRISC machine restart/halt/poweroff, idle, thread creation, process start, context switch integration, register dumps, and ELF core register export.

## Important APIs, Types, And Functions
Defines `current_thread_info_set[NR_CPUS]`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `arch_cpu_idle()`, `flush_thread()`, `show_regs()`, `copy_thread()`, `start_thread()`, `__switch_to()`, `dump_elf_thread()`, and `__get_wchan()`.

## Control Flow
`copy_thread()` builds user and kernel `pt_regs` frames on the new task stack and points `ksp` at the kernel frame. `start_thread()` clears registers and sets user PC/SP/SR. `__switch_to()` disables IRQs, saves/restores FPU, updates `current_thread_info_set`, calls assembly `_switch`, then restores IRQs.

## State And Persistence
Maintains per-CPU current-thread pointer, per-task saved kernel stack pointer, FPU state, and task register frames. Restart/poweroff may issue simulator `l.nop` commands.

## Dependencies And Integration Points
Depends on scheduler, task stacks, FPU helpers, OpenRISC SPRs, `entry.S` `_switch`/`ret_from_fork`, and signal/core dump ABI.

## Risks
Stack frame layout must match `entry.S`. `__get_wchan()` is unimplemented. Poweroff/restart fallbacks are simulator-specific and may not work on real hardware without sys-off handlers.

## Test Signals
Fork/clone/kernel-thread tests, exec register setup, context-switch/FPU stress, reboot/poweroff on simulator and board platforms, and core dump register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c

## Purpose
Provides the OpenRISC early device-tree scan hook.

## Important APIs, Types, And Functions
`early_init_devtree(void *params)` calls `early_init_dt_scan(params, __pa(params))` and then enables memblock resizing.

## Control Flow
`or1k_early_setup()` passes an FDT pointer here before `setup_arch()` unflattens and copies the device tree.

## State And Persistence
Initializes global early OF data and memblock memory reservations.

## Dependencies And Integration Points
Depends on `of_fdt`, `memblock`, and `__pa()` translation.

## Risks
The FDT pointer must be valid under early translation rules. Bad physical address conversion prevents memory and CPU discovery.

## Test Signals
Boot with external and built-in DTB, reserved-memory parsing, and memblock dump consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c

## Purpose
Implements OpenRISC ptrace regsets, register-offset lookup, stack access helpers, and syscall trace/audit hooks.

## Important APIs, Types, And Functions
`genregs_get/set()` expose GPRs, PC, and SR while ignoring writes to SR. Optional `fpregs_get/set()` exposes `fpcsr`. `task_user_regset_view()`, `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `arch_ptrace()`, `do_syscall_trace_enter()`, and `do_syscall_trace_leave()` complete the interface.

## Control Flow
Ptrace requests route through generic `ptrace_request()` after architecture detach cleanup. Syscall entry may ask ptrace to skip a syscall, then records audit arguments; syscall exit reports audit and ptrace single-step/syscall-exit events.

## State And Persistence
Reads and writes task `pt_regs` and thread FPU state. Clears syscall trace/single-step flags on detach.

## Dependencies And Integration Points
Depends on UAPI regset layout, audit, ptrace core, `entry.S` syscall tracing branches, and task stack layout.

## Risks
Regset size uses 32-bit word assumptions. Letting userspace change SR would be dangerous, so writes are ignored. Syscall skip returns `-1` as a bogus syscall number and relies on entry code bounds handling.

## Test Signals
GDB attach/detach, `PTRACE_GETREGSET`/`SETREGSET`, syscall trace skip tests, audit records, and stack dump helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c

## Purpose
Handles OpenRISC architecture boot setup: memory discovery/reservation, CPU feature discovery, early FDT selection, delay calibration, paging handoff, initrd handling, and `/proc/cpuinfo`.

## Important APIs, Types, And Functions
Key functions are `setup_memory()`, `setup_cpuinfo()`, `or1k_early_setup()`, `calibrate_delay()`, `setup_arch()`, and `cpuinfo_op` callbacks. Global `cpuinfo_or1k[NR_CPUS]` stores clock, core ID, and cache descriptors.

## Control Flow
`setup_arch()` reserves kernel/initrd/FDT memory, unflattens DT, records CPU info, initializes SMP CPU possible map, sets initial mm bounds, initializes jump labels before RO page lockdown, calls `paging_init()`, and exposes the command line.

## State And Persistence
Populates memblock reservations, global PFN limits, initrd state, CPU info, `loops_per_jiffy`, initial mm section bounds, and procfs CPU display state.

## Dependencies And Integration Points
Depends on OF/FDT, memblock, linker symbols, SMP setup, jump labels, paging, and OpenRISC SPR feature registers.

## Risks
Missing `clock-frequency` is warning-only in CPU info but fatal in delay calibration. `extract_value_bits()` appears unused and has a suspicious `(0 << width)` mask. Memory discovery assumes the kernel-containing DRAM range is the only main memory.

## Test Signals
Boot with/without initrd, DT CPU clock parsing, `/proc/cpuinfo`, memblock reservations, SMP CPU enumeration, and jump-label initialization before paging locks text RO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c

## Purpose
Implements OpenRISC signal-frame creation, `rt_sigreturn`, FPU signal state, syscall restart decisions, and userspace return work processing.

## Important APIs, Types, And Functions
Defines `struct rt_sigframe`, `_sys_rt_sigreturn()`, `restore_sigcontext()`, `setup_sigcontext()`, `get_sigframe()`, `setup_rt_frame()`, `handle_signal()`, `do_signal()`, and `do_work_pending()`.

## Control Flow
Signal delivery chooses user or alt stack, writes siginfo/ucontext/mask and a small `rt_sigreturn` trampoline, then redirects PC and arguments to the handler. `rt_sigreturn` validates frame alignment/access, restores signal mask, registers, FPU state, and alt stack. `do_signal()` handles syscall restart values before and after `get_signal()`.

## State And Persistence
Persists saved registers/FPU/mask on the user stack. Mutates live `pt_regs`, blocked signal mask, restart block, and optional FPU state.

## Dependencies And Integration Points
Depends on UAPI sigcontext/ucontext, usercopy, FPU helpers, syscall register ABI, `entry.S` return path, and `resume_user_mode_work()`.

## Risks
Signal-frame ABI is fragile. Kernel must clear `SPR_SR_SM` on restore to prevent user supervisor mode. Trampoline instruction encoding and syscall number must match the ABI.

## Test Signals
Signal delivery/return, SA_SIGINFO, altstack, syscall restart variants, ptrace interaction during signals, and FPU `fpcsr` preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c

## Purpose
Implements OpenRISC SMP CPU discovery/startup, IPI handling, CPU stop, SMP TLB shootdowns, and cross-CPU I-cache invalidation.

## Important APIs, Types, And Functions
State includes `ipi_irq`, `smp_cross_call`, `secondary_release`, `secondary_thread_info`, and `cpu_running`. Functions include `smp_init_cpus()`, `smp_prepare_cpus()`, `__cpu_up()`, `secondary_start_kernel()`, `handle_IPI()`, `arch_smp_send_reschedule()`, `set_smp_cross_call()`, call-function IPI senders, global `flush_tlb_*()`, and `smp_icache_page_inv()`.

## Control Flow
Boot CPU discovers CPU hardware IDs from DT, marks CPUs present, installs IPI callback, releases secondaries with `IPI_WAKEUP`, waits for completion, then synchronizes timers. Secondary CPUs set up `init_mm`, CPU info, clockevents, notify CPU core, sync timer, enable IPIs, mark online, and enter idle.

## State And Persistence
Maintains IPI IRQ/callback, secondary boot handshake variables, CPU online/present/possible masks, `current_pgd`, per-mm CPU masks, and synchronized timer state.

## Dependencies And Integration Points
Depends on OF CPU nodes, interrupt controller IPI driver, generic SMP call-function core, TLB/cacheflush APIs, and `head.S` secondary wait/start labels.

## Risks
If `smp_cross_call` is missing, CPUs cannot start. TLB shootdowns are synchronous and broad because local mm flush flushes all. `ipi_irq` can only be set once.

## Test Signals
SMP boot with multiple DT CPU nodes, IPI reschedule/call-function tests, CPU stop, TLB shootdown under mmap/mprotect, and cross-CPU icache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c

## Purpose
Adapts the OpenRISC unwinder to Linux `struct stack_trace` collection APIs.

## Important APIs, Types, And Functions
Implements `save_stack_trace()`, `save_stack_trace_tsk()`, and `save_stack_trace_regs()`, plus callbacks that only record reliable entries and optionally skip scheduler functions.

## Control Flow
For current task it starts near a local stack variable; for another task it pins the task stack, derives the saved kernel context from `thread_info->ksp`, unwinds, then drops the stack reference.

## State And Persistence
Fills caller-provided stack trace buffers. Does not persist internal state.

## Dependencies And Integration Points
Depends on `unwind_stack()`, scheduler stack helpers, `thread_info->ksp`, and stacktrace export APIs.

## Risks
If unwinder marks entries unreliable, traces can be empty. Deriving another task's SP depends on the context-switch frame layout.

## Test Signals
Stacktrace users such as lockdep, perf, WARN/Oops output, and task stack traces under `CONFIG_FRAME_POINTER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c

## Purpose
Synchronizes OpenRISC per-CPU tick timer counters during secondary CPU bring-up.

## Important APIs, Types, And Functions
Uses `initcount`, `count_count_start`, `count_count_stop`, `COUNTON`, and `NR_LOOPS`. Exports `synchronise_count_master()` and `synchronise_count_slave()`.

## Control Flow
Master and slave perform three atomic handshakes. The middle pass samples `initcount`; the final pass writes TTCR on both CPUs. Both schedule a near-future timer event before returning.

## State And Persistence
Temporarily uses atomic counters and persists synchronized TTCR values in hardware timers.

## Dependencies And Integration Points
Called from `__cpu_up()` and `secondary_start_kernel()`. Depends on timer APIs, barriers, atomics, and IRQ save/restore.

## Risks
Handshake assumes one secondary at a time. Broken barriers or missed atomic transitions can hang CPU bring-up. CPU0 can see a small time warp by design.

## Test Signals
SMP boot repeatedly, timer interrupt delivery soon after CPU online, and no hangs in counter synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sync-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c

## Purpose
Defines the OpenRISC syscall dispatch table.

## Important APIs, Types, And Functions
Defines `__SYSCALL` macros, aliases `sys_mmap2`, `sys_clone`, `sys_clone3`, and `sys_fork`, and creates `void *sys_call_table[__NR_syscalls]` from generated `asm/syscall_table_32.h`.

## Control Flow
`entry.S` indexes this table after validating the syscall number and jumps to the selected function.

## State And Persistence
Static table persists for kernel lifetime.

## Dependencies And Integration Points
Depends on generated syscall headers, OpenRISC wrappers in `entry.S`, and generic syscall declarations.

## Risks
Wrong aliases break fork/clone register preservation. Table type is `void *`, so function prototype checking is limited.

## Test Signals
Syscall number coverage, fork/clone/mmap tests, unknown syscall returning `-ENOSYS`, and generated table size matching `__NR_syscalls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c

## Purpose
Implements OpenRISC tick timer as a clocksource, per-CPU one-shot clockevent, and timer interrupt source.

## Important APIs, Types, And Functions
`openrisc_timer_set()`, `openrisc_timer_set_next()`, `openrisc_clockevent_init()`, `timer_interrupt()`, `openrisc_timer_read()`, `openrisc_timer_init()`, and `time_init()` are central. Per-CPU `clockevent_openrisc_timer` stores clockevent devices.

## Control Flow
`time_init()` verifies tick timer presence, registers a 32-bit continuous clocksource, initializes current CPU clockevent, initializes OF clocks, and probes timers. Timer interrupts acknowledge TTMR, enter IRQ context, invoke the clockevent handler, and exit.

## State And Persistence
Programs TTCR/TTMR SPRs and per-CPU clockevent state. Clocksource registration persists globally.

## Dependencies And Integration Points
Depends on `cpuinfo_or1k` clock frequency, clocksource/clockevents core, IRQ handling, OF clock init, and SMP broadcast support.

## Risks
Compare period uses only low 28 bits. Systems without TTMR panic. Timer ack disables interrupt bits while keeping continuous mode, so next-event programming must follow correctly.

## Test Signals
Clocksource registration, high-resolution timer behavior, scheduler ticks, SMP clockevent setup, and boot panic on no tick timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c

## Purpose
Handles OpenRISC traps and diagnostics: register/stack dumps, fatal kernel exceptions, user signals for fault classes, FPU exception decoding, and emulation of `lwa`/`swa` atomic instructions.

## Important APIs, Types, And Functions
Defines `lwa_flag` and `lwa_addr`; functions include `show_stack()`, `show_registers()`, `die()`, `unhandled_exception()`, `do_fpe_trap()`, `do_trap()`, `do_unaligned_access()`, `do_bus_fault()`, `do_illegal_instruction()`, and helpers for delay-slot PC adjustment and `lwa`/`swa` simulation.

## Control Flow
C exception handlers either force user signals or call `die()` in kernel mode. Illegal instruction handling recognizes `INSN_LWA` and `INSN_SWA`, simulates load/store conditional behavior using usercopy or exception table fixups, adjusts PC for delay slots, and sets SR flag on successful `swa`.

## State And Persistence
Maintains global `lwa_flag`/`lwa_addr` across emulated atomic instruction pairs. Reads and mutates live `pt_regs`, FPU status, and user memory.

## Dependencies And Integration Points
Called from `entry.S` exception stubs. Depends on FPU save/restore, exception tables, usercopy, unwinder, kallsyms, and OpenRISC instruction encodings.

## Risks
`lwa_flag` is global, not per-task/per-CPU, and is cleared in several entry paths; concurrency correctness relies on interrupts/context behavior. Delay-slot simulation is subtle. Kernel-mode bad accesses must find exception table fixups or die.

## Test Signals
Illegal instruction tests, user SIGFPE/SIGTRAP/SIGBUS/SIGILL delivery, atomic `lwa`/`swa` emulation under contention, delay-slot fault tests, and Oops register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c

## Purpose
Implements OpenRISC stack unwinding with frame-pointer-aware reliable mode and fallback stack scanning.

## Important APIs, Types, And Functions
Under `CONFIG_FRAME_POINTER`, `struct or1k_frameinfo` models previous FP, return address, and previous top. `or1k_frameinfo_valid()` validates frame chain and text address. `unwind_stack()` invokes caller callback for discovered return addresses. Without frame pointers, it scans stack words for kernel text addresses and marks them unreliable.

## Control Flow
Frame-pointer mode scans stack positions and only marks a hit reliable if the next expected frame pointer matches. Fallback mode linearly scans until `kstack_end()`.

## State And Persistence
No persistent state; observes stack memory.

## Dependencies And Integration Points
Used by traps and stacktrace code. Depends on task-stack helpers and kernel text address validation.

## Risks
Frame layout assumptions must match compiler ABI. Fallback mode can report false positives. Reliable stacktrace users may get no entries without frame pointers.

## Test Signals
Frame-pointer builds, Oops call traces, `save_stack_trace*()` consumers, and scheduler-stack filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h

## Purpose
Declares linker-provided initrd symbols for OpenRISC setup code.

## Important APIs, Types, And Functions
Under `CONFIG_BLK_DEV_INITRD`, declares `extern char __initrd_start, __initrd_end;`.

## Control Flow
No flow. `setup.c` reads these symbols to reserve and report initrd memory.

## State And Persistence
No state; exposes linker-symbol addresses.

## Dependencies And Integration Points
Depends on linker script/initrd placement and `setup.c`.

## Risks
Symbol declarations must match linker output. Wrong type/address use corrupts initrd reservation.

## Test Signals
Boot with initrd, correct initrd start/end reporting, and no overlap with kernel reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S

## Purpose
Defines the OpenRISC kernel link layout, output format, section order, and key linker symbols.

## Important APIs, Types, And Functions
Sets `LOAD_OFFSET`/`LOAD_BASE` to `PAGE_OFFSET`, chooses `elf32-or1k` or `elf32-or32`, defines `jiffies`, and lays out `_text`, `_stext`, `_etext`, `_s_kernel_ro`, `_e_kernel_ro`, `_sdata`, `_edata`, `__init_begin`, `__init_end`, BSS, `_end`, exception table, percpu, debug, modinfo, and discarded sections.

## Control Flow
The linker script has declarative build-time flow. Runtime code depends on section boundaries for memory reservation, RO mapping, and initial mm setup.

## State And Persistence
Determines the persistent in-memory kernel image layout.

## Dependencies And Integration Points
Uses generic vmlinux linker macros and OpenRISC page/cache/thread constants. Consumed by `setup.c`, `mm/init.c`, exception tables, and module/debug tooling.

## Risks
Alignment controls page permissions; wrong `_s_kernel_ro`/`_e_kernel_ro` boundaries can leave text writable or data read-only. Output-format mismatch breaks boot loaders and tools.

## Test Signals
Link success, section boundary inspection, RO text after paging init, exception table fixups, and boot on both OR1K output-format configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile

## Purpose
Builds OpenRISC architecture library routines.

## Important APIs, Types, And Functions
Adds `delay.o`, `string.o`, `memset.o`, and `memcpy.o` to `obj-y`.

## Control Flow
Kbuild compiles these helpers into the kernel image.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Supports delay loops, usercopy, clear_user, memset, and memcpy declarations/exports.

## Risks
Removing objects breaks low-level architecture APIs and module exports.

## Test Signals
Full kernel link, usercopy tests, delay tests, and string/memory operation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c

## Purpose
Implements precise OpenRISC busy-wait delay loops using the tick timer counter.

## Important APIs, Types, And Functions
`read_current_timer()` returns `get_cycles()`. `__delay()` spins until a cycle delta elapses. `__const_udelay()`, `__udelay()`, and `__ndelay()` scale micro/nanosecond inputs through `loops_per_jiffy` and `HZ`.

## Control Flow
Delay calls sample `get_cycles()` and loop with `cpu_relax()` until unsigned delta reaches the requested count.

## State And Persistence
Reads TTCR and `loops_per_jiffy`; no persistent state.

## Dependencies And Integration Points
Depends on `timex.h`, delay API, calibrated loops from `setup.c`, and exported symbols for modules.

## Risks
Accuracy depends on CPU clock frequency and running tick timer. Large delays rely on wrap-safe arithmetic but still busy-wait.

## Test Signals
Delay calibration output, timer-based delay tests, driver polling delays, and module references to exported delay helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/memcpy.c

## Purpose
Provides OpenRISC optimized `memcpy()`.

## Important APIs, Types, And Functions
Exports `memcpy()`. Under `CONFIG_OR1K_1200`, uses 32-byte word-copy unrolling when source/destination are word-aligned and byte-copy unrolling otherwise. Generic variant performs word copies for aligned prefixes and byte copies for the remainder.

## Control Flow
The function branches on alignment, copies word blocks when possible, then copies remaining bytes, returning the original destination.

## State And Persistence
Mutates destination memory only.

## Dependencies And Integration Points
Declared by `asm/string.h`, built by `lib/Makefile`, and exported for modules.

## Risks
No overlap handling; callers needing overlap must use `memmove`. Casts assume 32-bit pointer truncation is safe for OpenRISC. Alignment logic must avoid unaligned word traps.

## Test Signals
Kernel string tests across alignments/sizes, module use, boot memory copies, and OR1K_1200-specific performance/correctness checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/memset.S

## Purpose
Implements hand-optimized OpenRISC `memset()`.

## Important APIs, Types, And Functions
Global `memset` takes `r3` destination, `r4` byte value, and `r5` length; returns destination in `r11`.

## Control Flow
The routine exits on zero length, truncates and expands the byte to a 32-bit repeated word when nonzero, aligns the destination with byte stores, performs word stores while at least four bytes remain, then stores trailing bytes.

## State And Persistence
Mutates destination memory. No global state.

## Dependencies And Integration Points
Declared by `asm/string.h`, exported in `or32_ksyms.c`, and used by kernel memory initialization and modules.

## Risks
Assembly ABI must preserve caller expectations. Alignment and tail-copy branches must handle small sizes without underflow. Nonstandard comments use C++ style but assembler accepts them in this source context.

## Test Signals
Memset tests for zero length, all alignments, small sizes, large sizes, and module references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S

## Purpose
Implements OpenRISC bulk usercopy and clear-user assembly helpers with exception-table recovery.

## Important APIs, Types, And Functions
`__copy_tofrom_user(void *to, const void *from, unsigned long size)` copies byte-by-byte and returns bytes not copied. `__clear_user(void *addr, unsigned long size)` zeros user memory and returns bytes not cleared.

## Control Flow
Both routines save argument registers, loop one byte at a time, and use `__ex_table` entries for faulting load/store labels. Fixup jumps to the common exit, returning the remaining byte count.

## State And Persistence
Mutates destination memory and returns partial-copy counts. No persistent state.

## Dependencies And Integration Points
Called from `uaccess.h` raw copy/clear wrappers and exported in `or32_ksyms.c`. Depends on page-fault exception-table fixup handling.

## Risks
Byte-at-a-time implementation is simple but slow. Correct remaining-byte count on fault is ABI-visible. Exception table entries must match faulting labels.

## Test Signals
Usercopy fault injection, partial-copy return values, clear_user tests, and module usercopy helper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/Makefile

## Purpose
Builds OpenRISC memory-management implementation objects.

## Important APIs, Types, And Functions
Adds `fault.o`, `cache.o`, `tlb.o`, `init.o`, and `ioremap.o`.

## Control Flow
Kbuild compiles these into the architecture mm subsystem.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Provides page fault, cache maintenance, TLB flushing/context switch, boot paging, fixmap, and early ioremap page table allocation.

## Risks
Object omissions break boot, page faults, cache coherency, or device mappings.

## Test Signals
OpenRISC build/link, boot through paging init, page-fault handling, ioremap, and cache/TLB operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c

## Purpose
Implements OpenRISC cache presence checks, D-cache flush/invalidate, I-cache invalidate, and executable mapping cache synchronization.

## Important APIs, Types, And Functions
`cpu_cache_is_present()`, `local_dcache_page_flush()`, `local_icache_page_inv()`, `local_dcache_range_flush()`, `local_dcache_range_inv()`, `local_icache_range_inv()`, and `update_cache()` are central.

## Control Flow
Range helpers loop over cache-line-sized physical addresses and write cache-control SPRs. `update_cache()` marks folios clean using `PG_dc_clean`; for executable VMAs it synchronizes I-cache/D-cache for dirty folio pages.

## State And Persistence
Mutates hardware cache state and folio `PG_dc_clean` flag. No private global state.

## Dependencies And Integration Points
Depends on UPR cache bits, cache SPRs, `L1_CACHE_BYTES`, folio flags, and cacheflush APIs used by mmap, DMA, and text patching.

## Risks
Cache line size must match hardware. `PG_dc_clean` state controls whether executable mappings get synchronized. Physical address ranges must be line-aligned enough for hardware expectations.

## Test Signals
Executable mmap after writes, text patching, DMA coherency, cacheinfo consistency, and platforms with absent I-cache/D-cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c

## Purpose
Handles OpenRISC page faults, including user faults, kernel faults with exception-table fixups, stack growth, vmalloc page table synchronization, OOM/SIGBUS/SIGSEGV paths, and executable permission checks.

## Important APIs, Types, And Functions
Global `current_pgd[NR_CPUS]` tracks active top-level page tables for low-level handlers. `do_page_fault()` is the main handler. Macros define TLB entry count and address offset helpers.

## Control Flow
Kernel vmalloc faults can copy top-level mappings from `init_mm` without taking locks. User faults enable IRQs, find/expand VMA, validate write/read/execute permissions, call `handle_mm_fault()`, process retry/completed/error results, and signal or die as needed. Kernel faults search exception tables before Oops.

## State And Persistence
May expand VMAs, populate page tables, update current faulting task state, and synchronize `current_pgd` mappings for vmalloc. Signals persist to task pending signal state.

## Dependencies And Integration Points
Called from `entry.S`. Depends on `mmu_context`, exception tables, perf fault events, signal delivery, and vmalloc global mappings.

## Risks
The kernel IRQ reenable test uses `if (regs->sr && (SPR_SR_IEE | SPR_SR_TEE))`, which is broad rather than masking explicitly. Vmalloc fault synchronization assumes two-level page table behavior. Execute permission check uses OpenRISC page-prot bits directly.

## Test Signals
User read/write/exec faults, stack growth, kernel usercopy fixups, vmalloc faults, OOM fault handling, SIGBUS mappings, and SMP current_pgd behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c

## Purpose
Initializes OpenRISC paging, maps RAM, patches final TLB miss vectors, manages fixmap mappings, marks kernel RO pages, and defines vm protection mappings.

## Important APIs, Types, And Functions
`arch_zone_limits_init()`, `map_ram()`, `paging_init()`, `mem_init()`, `map_page()`, `__set_fixmap()`, `protection_map`, and `DECLARE_VM_GET_PAGE_PROT` are key. Global `mem_init_done` gates early PTE allocation elsewhere.

## Control Flow
`paging_init()` clears `swapper_pg_dir`, initializes `current_pgd`, maps all memblock ranges via two-level page tables, patches vector slots at `0x900` and `0xa00` to runtime TLB handlers, invalidates I-cache blocks, and flushes TLBs so new RO flags take effect.

## State And Persistence
Creates kernel page tables, maps physical memory, sets RO permissions for linker-defined kernel RO range, updates low exception vectors, sets `mem_init_done`, and manages fixmap PTEs.

## Dependencies And Integration Points
Depends on memblock, linker symbols, `swapper_pg_dir` from `head.S`, TLB miss handlers, cache/TLB flush APIs, fixmap, and generic VM protection code.

## Risks
Hardcoded two-level page table assumptions are enforced by panic. Vector self-modification before RO lockdown is delicate. Fixmap clearing uses `pgprot_val(prot) == 0` semantics.

## Test Signals
Boot through paging init, kernel text RO enforcement, fixmap users such as early console/text poke, RAM mapping across memblock ranges, and page protection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c

## Purpose
Provides OpenRISC kernel PTE page allocation for ioremap, including early boot before normal memory allocation is ready.

## Important APIs, Types, And Functions
`pte_alloc_one_kernel(struct mm_struct *mm)` returns `__pte_alloc_one_kernel()` after `mem_init_done`, otherwise allocates a page from memblock.

## Control Flow
Ioremap/fixmap page-table creation calls this allocator. Early callers get memblock-backed PTE pages; later callers use normal kernel PTE allocation.

## State And Persistence
Allocates PTE pages that persist as kernel page tables.

## Dependencies And Integration Points
Depends on `mem_init_done` from `mm/init.c`, memblock, vmalloc/ioremap, pgalloc, and TLB flushing by callers.

## Risks
Early allocations are never freed through normal paths. Incorrect `mem_init_done` timing can call unavailable allocators or leak memblock pages.

## Test Signals
Early serial console ioremap, later driver ioremap, fixmap setup, and boot with `mem_init_done` transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c

## Purpose
Implements local OpenRISC TLB invalidation, mm context switching, and dummy mm context lifecycle.

## Important APIs, Types, And Functions
`local_flush_tlb_all()`, `local_flush_tlb_page()`, `local_flush_tlb_range()`, `local_flush_tlb_mm()`, `switch_mm()`, `init_new_context()`, and `destroy_context()` are central. The code uses `SPR_DTLBEIR`/`SPR_ITLBEIR` when available and falls back to clearing match registers.

## Control Flow
Full flush loops over IMMU set count and clears DTLB/ITLB match registers. Page/range flushes either write invalidate-by-effective-address SPRs or clear computed set entries. `switch_mm()` updates mm CPU masks, stores `current_pgd[cpu]`, and flushes all previous mappings because context IDs are not implemented.

## State And Persistence
Invalidates hardware TLBs, updates `current_pgd`, and sets `mm->context` to `NO_CONTEXT`.

## Dependencies And Integration Points
Depends on SPR MMU config bits, `current_pgd` from fault handling, generic scheduler `switch_mm`, and TLB flush declarations.

## Risks
`NUM_DTLB_SETS` appears to read `SPR_IMMUCFGR` instead of `SPR_DMMUCFGR`, a potential geometry bug. No ASID/context support means frequent full flushes. No-EIR fallback assumes single-way behavior.

## Test Signals
Context-switch memory isolation, TLB range/page invalidation, hardware with/without TLBEIR, SMP shootdowns, and page-table permission changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/parisc/Kbuild

## Purpose
Declares PA-RISC architecture subdirectories built by Kbuild.

## Important APIs, Types, And Functions
Adds `mm/`, `kernel/`, `math-emu/`, and `net/` to `obj-y`, and lists `boot` as a non-recursive subdir.

## Control Flow
Kbuild descends into these directories during architecture builds; boot artifacts are handled separately.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Works with `arch/parisc/Makefile` and per-directory Makefiles for core architecture subsystems.

## Risks
Directory omissions drop required architecture code or boot image generation support.

## Test Signals
PA-RISC allmodconfig/defconfig builds and boot image target availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/parisc/Kconfig

## Purpose
Defines the PA-RISC architecture configuration surface, selected generic capabilities, CPU families, page sizes, SMP, compatibility mode, and kexec support.

## Important APIs, Types, And Functions
Top-level `config PARISC` selects architecture features such as cache aliasing, DMA ops, strict RWX, perf, PCI, seccomp filter, eBPF JIT, stack walking, clockevents, kgdb, kprobes, dynamic ftrace, and endian/MMU defaults. CPU choices include `PA7000`, `PA7100LC`, `PA7200`, `PA7300LC`, and `PA8X00`; derived configs include `PA11`, `PA20`, `64BIT`, page-size choices, `SMP`, `IRQSTACKS`, `COMPAT`, and `NR_CPUS`.

## Control Flow
Kconfig dependency resolution selects architecture capabilities and exposes user choices. Build files and C code compile conditionally from these symbols.

## State And Persistence
No runtime state, but `.config` output persists build-time architecture behavior including ABI width, page size, CPU count, and enabled mitigations/features.

## Dependencies And Integration Points
Integrated with generic kernel subsystems for MM, DMA, tracing, BPF, PCI, RTC, kexec, modules, and scheduler topology.

## Risks
Selects must match actual architecture implementations. Some page-size options are marked `BROKEN`; enabling them would risk memory-management failures. 64-bit notes state there is no 64-bit userland, so compat handling is important.

## Test Signals
Kconfig olddefconfig for 32-bit and 64-bit PA-RISC, SMP builds, BPF JIT/tracing builds, page-size option gating, and kexec configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/Makefile

## Purpose
Controls PA-RISC architecture compiler/linker flags, build directories, boot image targets, decompressor selection, vdso preparation, install targets, and cleanup.

## Important APIs, Types, And Functions
Sets `boot := arch/parisc/boot`, default `KBUILD_IMAGE`, 32/64-bit compiler flags, ABI flags, alignment and long-call options, `head-y`, core/libs/drivers paths, `KBUILD_CFLAGS_KERNEL`, `KBUILD_AFLAGS_MODULE`, and boot aliases such as `bzImage`, `zImage`, `Image`, and `vmlinuz`.

## Control Flow
Kbuild evaluates architecture width and config options, constructs flags, builds vDSO offsets when not external-module builds, routes image targets into boot sub-Makefiles, and defines install/zinstall behavior.

## State And Persistence
No runtime state; persists build choices in produced objects/images and generated vDSO offset headers.

## Dependencies And Integration Points
Depends on compiler support for PA-RISC flags, boot directory Makefile, kernel/vdso Makefiles, and install tooling.

## Risks
Wrong ABI flags produce unbootable or incompatible kernels. Long-call and huge-kernel decisions affect link reachability. Build target aliases must match boot loader expectations.

## Test Signals
32-bit and 64-bit PA-RISC builds, compressed/uncompressed images, module builds, vdso_prepare, `make install`, and clean targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile

## Purpose
Builds PA-RISC boot image artifacts.

## Important APIs, Types, And Functions
Defines targets for `image`, `bzImage`, and `compressed/vmlinux`. `image` copies `vmlinux`; `bzImage` copies either uncompressed `vmlinux` or compressed `boot/compressed/vmlinux` depending on `CONFIG_KERNEL_UNCOMPRESSED`; compressed target invokes the compressed subdirectory.

## Control Flow
Top-level PA-RISC image targets recurse here. Kbuild uses `$(call if_changed,shipped)` for copy-style outputs and `$(Q)$(MAKE)` for compressed image generation.

## State And Persistence
Produces boot image files under `arch/parisc/boot`.

## Dependencies And Integration Points
Depends on top-level `vmlinux`, compressed boot Makefile, and `CONFIG_KERNEL_UNCOMPRESSED`.

## Risks
Incorrect dependency selection can ship stale compressed or uncompressed images. Boot target names must match `arch/parisc/Makefile` aliases.

## Test Signals
Build `image`, `bzImage`, and `vmlinuz` with compressed and uncompressed kernel configurations; verify output timestamps and boot loader consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/boot/Makefile -->
