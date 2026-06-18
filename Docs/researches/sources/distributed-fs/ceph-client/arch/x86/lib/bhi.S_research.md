# sources/distributed-fs/ceph-client/arch/x86/lib/bhi.S

Purpose: provides the `__bhi_args` code array used by FineIBT Branch History Injection mitigation paths. It supplies carefully aligned return stubs that conditionally sanitize argument registers before returning, with intentional `ud2` sites placed for short conditional branches.

Important APIs/functions: defines `__bhi_args` in `.noinstr.text`, local labels `__bhi_args_0` through `__bhi_args_7`, global `__bhi_args_end`, and conditional code under `CONFIG_FINEIBT_BHI`. The stubs use `ANNOTATE_NOENDBR`, `UNWIND_HINT_FUNC`, `ANNOTATE_UNRET_SAFE`, and `ANNOTATE_REACHABLE`.

Control flow: when FineIBT BHI is enabled, each 32-byte-aligned element checks `jne` to an intentional `ud2` trap and otherwise uses `cmovne %rax, <arg register>` for an increasing number of argument registers before returning. The preamble is expected to enter with ZF set and `%eax` zero. Elements 1 and 5 include alignment holes so two nearby `ud2` sites can be reached by short conditional jumps.

State and persistence behavior: no persistent state. It transiently modifies argument registers on paths where condition flags select the `cmovne` operations and returns through annotated mitigation-safe paths.

Dependencies/integration points: included only in the 64-bit library build. Integrated with x86 speculation mitigation infrastructure, objtool/unwind annotations, FineIBT, and noinstr constraints.

Risks: alignment and label layout are part of the contract; small edits can break branch reachability, objtool validation, or mitigation properties. Because it is in `.noinstr.text`, instrumentation must not be introduced. Flag assumptions from callers are critical.

Test signals: objtool noinstr/unwind validation, builds with and without `CONFIG_FINEIBT_BHI`, disassembly/layout inspection for 32-byte element spacing and `ud2` placement, and mitigation selftests where available.
