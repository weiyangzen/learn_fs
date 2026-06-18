<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c

## Purpose

`test_shadow_stack.c` tests core x86 userspace CET shadow-stack behavior without relying on libc shadow-stack enablement. It covers `arch_prctl` enable/disable, `map_shadow_stack`, WRSS writes, shadow-stack faults, guard gaps, `mprotect`, GUP, userfaultfd, ptrace NT_X86_SHSTK state, 32-bit signal interaction, and return uprobes.

## Important APIs, Types, and Functions

Important interfaces include `ARCH_PRCTL()` inline syscall, `create_shstk()`, `write_shstk()`, `get_ssp()`, `try_shstk()`, `test_shstk_pivot()`, `test_shstk_faults()`, `test_shstk_violation()`, `test_gup()`, `test_mprotect()`, `test_userfaultfd()`, guard-gap tests, `sigaction32()`, `test_32bit()`, `test_uretprobe()`, and `test_ptrace()`. Kernel APIs exercised include `__NR_map_shadow_stack`, `ARCH_SHSTK_ENABLE/DISABLE/STATUS`, `ARCH_SHSTK_WRSS`, `/proc/self/mem`, `userfaultfd`, `perf_event_open` uprobes, and `PTRACE_GETREGSET/SETREGSET` with `NT_X86_SHSTK`.

## Control Flow and State

`main()` enables shadow stack, disables and reenables it to test control ABI, enables WRSS, then runs each subtest in sequence. Signal handlers fix corrupted shadow-stack entries or convert expected faults into success paths. Global state tracks current shadow-stack pointer, saved SSP value, access mode, file descriptors, and `segv_triggered`. Most subtests allocate and release shadow-stack mappings; the final cleanup disables shadow stack before returning where necessary.

## Dependencies and Integration Points

The file depends on GCC CET instruction support, x86 CET-capable kernel and hardware, raw arch prctl support, `asm/mman.h`, `linux/userfaultfd.h`, `linux/perf_event.h`, ptrace regsets, `/sys/bus/event_source/devices/uprobe`, and 32-bit compat signal behavior. It is a high-value integration test across mm, signal, ptrace, perf uprobes, and x86 arch code.

## Risks and Test Signals

Risks include missing guard pages, writable shadow stacks through ordinary writes, broken WRSS or COW behavior, `mprotect` permission confusion, userfaultfd mishandling, invalid ptrace SSP acceptance, 32-bit signal crashes, and uretprobe return-address corruption. Passing output prints `[OK]` for each subtest; skips occur when shadow stack, WRSS, userfaultfd, or uprobes are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_shadow_stack.c -->
