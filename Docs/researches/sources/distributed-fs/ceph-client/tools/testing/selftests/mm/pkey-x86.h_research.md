# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-x86.h

Purpose: x86/i386 support layer for pkey tests, centered on PKRU register access, XSAVE layout discovery, signal context offsets, and CPUID feature detection.

Important APIs and functions: defines signal context macros, `NR_PKEYS`, `PKEY_BITS_PER_PKEY`, page sizes, `__read_pkey_reg()`/`__write_pkey_reg()` using RDPKRU/WRPKRU opcodes, `cpu_has_pkeys()`, `cpu_max_xsave_size()`, `pkey_reg_xstate_offset()`, and `expect_fault_on_read_execonly_key()`.

Control flow and state: included by `pkey-helpers.h` on x86. Main tests use CPUID checks, signal handlers clear PKRU in saved XSAVE context, and ptrace tests use the same offsets with `NT_X86_XSTATE`.

Dependencies and risks: requires PKU/OSPKE, CPUID, XSAVE layout stability, and compiler support for related builtins in the main test. Hardcoded `si_pkey` offsets are ABI-sensitive.
