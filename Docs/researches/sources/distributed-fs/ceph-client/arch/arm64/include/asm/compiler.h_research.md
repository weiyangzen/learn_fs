## sources/distributed-fs/ceph-client/arch/arm64/include/asm/compiler.h

Purpose: arm64 compiler integration for assembly preambles, pointer-auth stripping, and return-address handling.

Important APIs/types/functions: defines `ARM64_ASM_PREAMBLE`, `xpaclri(ptr)`, `ptrauth_strip_kernel_insn_pac`, `ptrauth_strip_user_insn_pac`, and overrides `__builtin_return_address` under pointer-auth configurations.

Control flow: `xpaclri` emits a hint-form pointer-auth strip instruction with fixed register usage; the return-address macro strips PAC from nonzero return addresses.

State and persistence: stateless pointer transformations.

Dependencies and integration: depends on assembler architecture features and pointer-auth config. Used by unwinding, tracing, ftrace, kprobes, and code inspecting instruction pointers.

Risks: incorrect PAC stripping breaks stack traces, profiling, and security instrumentation. Test signals are pointer-auth boot tests, unwinder tests, ftrace/perf/kprobe traces, and compiler compatibility builds.
