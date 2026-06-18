# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_syscall.c

## Purpose
x86_64-focused tests for syscall-backed optimized uprobes/uretprobes, register preservation, kernel test-module register modification, uretprobe syscall misuse handling, trampoline mapping, shadow stack compatibility, attach/detach races, and direct `uprobe` syscall error behavior.

## APIs, Types, and Functions
Public entry point `test_uprobe_syscall()` calls `__test_uprobe_syscall()` on x86_64 and skips elsewhere. Helpers include naked trigger functions, `test_uprobe_regs_equal()`, `write_bpf_testmod_uprobe()`, `test_regs_change()`, `test_uretprobe_syscall_call()`, trampoline discovery helpers, `test_uprobe_legacy()`, `test_uprobe_multi()`, `test_uprobe_session()`, `test_uprobe_usdt()`, `test_uretprobe_shadow_stack()`, race workers, and `test_uprobe_error()`.

## Control Flow, State, and Persistence
Register tests attach uprobes/uretprobes to a self function, trigger optimization, run assembly that snapshots registers, and compare BPF-observed registers with before/after snapshots. The test-module path writes an offset to `/sys/kernel/bpf_testmod_uprobe`, triggers a probe that modifies registers, then unregisters. Uretprobe syscall misuse forks a child that invokes the uretprobe syscall directly and expects SIGILL without executing BPF. Optimized attach tests inspect patched NOP sites for call instructions into `[uprobes-trampoline]`, destroy links, and verify trampoline mapping persists. Shadow stack mode reruns the main cases with CET shadow stack enabled when available. Race test alternates attach/detach with trigger threads for a configurable duration and validates the USDT semaphore is inactive at the end.

## Dependencies and Integration
Depends on x86_64 assembly, arch prctl shadow-stack constants, raw syscall numbers, `/proc/self/maps`, BPF test module sysfs file, libbpf uprobe and uprobe_multi APIs, USDT macros, and generated skeletons.

## Risks and Test Signals
Risks include x86-only assumptions, compiler control-flow protection altering instruction layout, shadow stack availability, test module availability, race nondeterminism, and raw syscall number drift. Signals are register equality/modification assertions, child SIGILL, expected trampoline mapping and patched instruction bytes, no active race semaphore after attach/detach stress, and direct `uprobe` syscall returning `ENXIO`.
