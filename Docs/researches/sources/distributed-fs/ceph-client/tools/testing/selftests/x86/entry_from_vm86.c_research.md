# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/entry_from_vm86.c

## Purpose

`entry_from_vm86.c` tests kernel entry and signal paths from vm86 mode. It exercises exceptions, syscall-like instructions, interrupt handling, VIP/IF behavior, UMIP instruction emulation, null pointer execution, and fork cleanup from a vm86-capable process.

## Important APIs, Types, and Functions

It uses `vm86(VM86_ENTER, ...)`, `struct vm86plus_struct`, VM86 return macros, signal handlers, and 16-bit inline assembly blobs. Important helpers are `sighandler()`, `do_test()`, `do_umip_tests()`, and the assembly labels `vmcode_bound`, `vmcode_sysenter`, `vmcode_syscall`, `vmcode_sti`, `vmcode_int3`, `vmcode_int80`, `vmcode_popf_hlt`, `vmcode_umip`, `vmcode_umip_str`, and `vmcode_umip_sldt`.

## Control Flow

`main()` maps executable memory at `0x10000`, copies the 16-bit vm86 test code, initializes segment registers and stack, and runs a series of `do_test()` calls. Each call sets vm86 EIP, enters vm86 mode, handles skips for unsupported/disallowed vm86, prints the exit reason, and verifies the expected VM86 type/argument unless the expected type is `-1`. UMIP tests compare emulated SMSW/SIDT/SGDT results across addressing modes and expect STR/SLDT to signal. The final null pointer case expects SIGSEGV, and a fork sanity check ensures no cleanup failure.

## State and Persistence Behavior

State is process-local mapped low memory, vm86 register state, and signal flags. No persistence exists.

## Dependencies and Integration Points

It is 32-bit-only in the Makefile and requires kernel `vm86` support and permission. It integrates with x86 signal-frame conventions and UMIP emulation behavior.

## Risks and Edge Cases

Modern 64-bit-only kernels may skip due to `ENOSYS` or `EPERM`. The test maps executable low memory at a fixed address. Some outcomes vary by CPU feature, such as SYSENTER behavior on non-SEP CPUs, and the test avoids strict checking for those cases.

## Test Signals

Pass signals are expected VM86 exit reasons for #BR, SYSCALL, STI, POPF, INT3, INT80, UMIP, and null execution, consistent UMIP emulation results, receipt of SIGSEGV for null execution, and zero accumulated errors.
