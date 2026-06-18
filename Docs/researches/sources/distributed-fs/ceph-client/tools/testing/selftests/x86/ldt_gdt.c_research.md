# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ldt_gdt.c

## Purpose

`ldt_gdt.c` validates x86 LDT and GDT descriptor installation, validation, invalidation, fork/exec semantics, cross-CPU LDT invalidation, and segment register clearing when `set_thread_area` removes GDT entries.

## Important APIs, Types, and Functions

It uses `modify_ldt`, 32-bit `set_thread_area` via `int $0x80`, `struct user_desc`, `lsl`, `lar`, segment register loads, futexes, pthreads, CPU affinity, signals, fork/exec, and `arch_prctl` on x86_64 for FS/GS base restoration. Important helpers include `check_invalid_segment()`, `check_valid_segment()`, `install_valid_mode()`, `install_valid()`, `install_invalid()`, `safe_modify_ldt()`, `fail_install()`, `do_simple_tests()`, `threadproc()`, `fix_sa_restorer()`, `do_multicpu_tests()`, `finish_exec_test()`, `do_exec_test()`, `setup_counter_page()`, `invoke_set_thread_area()`, `setup_low_user_desc()`, and `test_gdt_invalidation()`.

## Control Flow

`main()` handles the exec-child mode by checking LDT entry 0 is invalid after exec. Normal execution maps a low counter page, tries to allocate a GDT entry with `set_thread_area`, runs descriptor installation tests for many code/data, present/not-present, page-limit, 16/32-bit, conforming, read-only, expand-down, usable, and long-mode combinations, checks invalid entries, tests fork inheritance of LDT entries, stress-installs up to 8192 LDT entries, verifies invalid high entry rejection, and tests deletion edge cases. It then runs cross-CPU invalidation by loading an LDT stack selector while a helper thread clears the LDT entry. It runs an exec test to ensure LDT is not inherited, and finally, if a GDT entry is available, tests that clearing it invalidates DS/ES/FS/GS and zeroes FS/GS bases as expected.

## State and Persistence Behavior

State is process-local descriptor table entries, segment registers, mapped low memory, thread/futex state, signal handlers, CPU affinity, and child process state. No files are persisted, but `/proc/self/exe` is execed for the exec inheritance test.

## Dependencies and Integration Points

It depends on x86 descriptor instructions, `modify_ldt` availability for full LDT coverage, `set_thread_area` for GDT coverage, 32-bit syscall ABI support for GDT tests, multiple CPUs for cross-CPU invalidation coverage, and signal behavior around invalid stack selectors.

## Risks and Edge Cases

Some kernels disable `modify_ldt`, causing skips for large portions. Cross-CPU invalidation requires CPU 0 and CPU 1 affinity; single-CPU systems skip it. The test deliberately loads SS/FS/GS with descriptors that may become invalid, relying on signal recovery. The glibc `sa_restorer` workaround is needed on i386 to avoid unrelated signal-frame failures.

## Test Signals

Pass signals include expected AR/limit values from LAR/LSL, invalid descriptors staying invalid, successful fork inheritance but exec cleanup, all cross-CPU invalidation iterations faulting safely, and DS/ES/FS/GS clearing plus FSBASE/GSBASE zeroing after GDT entry deletion.
