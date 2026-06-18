<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c

## Purpose

`sigreturn.c` is a comprehensive x86 signal-return and exit-to-userspace ABI regression test. It exercises `sigreturn(2)`, IRET, SYSRET-adjacent state restoration, segment selectors, stack pointer restoration, espfix behavior, and strict SS restore semantics.

## Important APIs, Types, and Functions

The file defines local copies of ucontext SS flags, LDT/GDT descriptor setup, an `int3` trampoline, selector helpers `GDT3()`, `LDT3()`, `cs_bitness()`, and `is_valid_ss()`. `setup_ldt()` creates 16-bit code/data and not-present segments with `modify_ldt` and probes `set_thread_area`. `sigusr1()` edits the signal context to request specific CS/SS/SP/IP values. `sigtrap()` records resulting registers and restores the original context. `test_valid_sigreturn()`, `test_bad_iret()`, and `test_nonstrict_ss()` implement the core checks.

## Control Flow and State

`main()` records current CS/SS, builds LDT entries, installs an alternate stack and signal handlers, then runs valid and invalid sigreturn cases. Valid cases return through the `int3` trampoline and are validated in the SIGTRAP handler. Invalid cases expect SIGSEGV, SIGBUS, or SIGILL after IRET failure. Global state stores initial, requested, and resulting gregsets, requested selectors, trap metadata, and error counts.

## Dependencies and Integration Points

The test depends on x86 segmentation, `asm/desc_defs.h`, `asm/ldt.h`, glibc ucontext layouts, `helpers.h`, altstack signal delivery, and kernel compatibility support for 16-bit and 32-bit segments. It directly targets historical CVE classes around espfix and malformed sigreturn frames.

## Risks and Test Signals

Risks include lost high stack-pointer bits, incorrect SS restore under `UC_STRICT_RESTORE_SS`, accepting invalid GDT/LDT descriptors, wrong trap reporting, and kernel stack leaks through espfix failures. Passing cases print register validation success or expected exception class; failures are register mismatches, missing signals, or incorrect strict SS handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigreturn.c -->
