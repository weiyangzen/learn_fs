# sources/distributed-fs/ceph-client/arch/x86/include/asm/user.h

Purpose: common x86 user ABI header selecting 32-bit or 64-bit legacy `struct user` layouts and defining extended xstate structures for ptrace/core dump consumers.

Important APIs/types/functions: includes `user_32.h` or `user_64.h`; defines `struct user_ymmh_regs`, `struct user_xstate_header`, `USER_XSTATE_FX_SW_WORDS`, `USER_XSTATE_XCR0_WORD`, and `struct user_xstateregs`.

Control flow: compile-time selection chooses native `struct user` ABI layout. Extended xstate layout mirrors processor XSAVE layout for NT_X86_XSTATE notes and ptrace, with software words carrying OS-enabled xstate mask.

State/persistence: no kernel runtime state. The structures describe serialized register state visible to debuggers and core dump readers.

Dependencies/integration: depends on arch integer types and native user layout headers. Integrated with ptrace, ELF core notes, debuggers, crash tools, and xsave feature enumeration.

Risks/test signals: layout drift breaks user-space debuggers and core dump parsing. Test ptrace GET/SETREGSET for xstate, core dump NT_X86_XSTATE notes, AVX/YMM state visibility, and CPUID-reported xsave size compatibility.
