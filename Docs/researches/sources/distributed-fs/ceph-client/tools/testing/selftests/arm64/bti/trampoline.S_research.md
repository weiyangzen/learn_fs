# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/trampoline.S

Purpose: indirect branch/call trampolines used to enter BTI test stubs with different branch types.

Important APIs/types/functions: `call_using_br_x0()` branches via `br x0`; `call_using_br_x16()` moves target to `x16` then branches; `call_using_blr()` uses PAC prologue/epilogue and `blr x0`.

Control flow: each trampoline receives a function pointer and transfers control, returning to caller for `blr` paths or via target return.

State and persistence: saves/restores frame pointer/link register in `call_using_blr`; emits feature note.

Dependencies/integration: declared in `btitest.h` and used by `test.c`.

Risks and test signals: branch register choice influences PSTATE.BTYPE and expected BTI landing compatibility.
