# sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-branch.h

Purpose: This header declares s390 speculative-execution branch mitigation controls and expoline indirect-jump thunk symbols.

Important APIs/types/functions: `nospec_disable`, `nobp`, `nobp_enabled()`, `nospec_init_branches()`, `nospec_auto_detect()`, `nospec_revert()`, `nospec_uses_trampoline()`, and `__s390_indirect_jump_r1..r15()` are the main declarations.

Control flow: Boot mitigation code detects facility support and command-line policy, initializes or reverts indirect branch mitigation sites, and thunk-aware code branches through register-specific expoline symbols when enabled.

State and persistence: Persistent state includes global mitigation flags and patched branch sites in `.s390_indirect_branches`; thunk text symbols persist in kernel/module text.

Dependencies and integration points: It depends on facility bit 82, compiler expoline mode, alternatives/text patching, and assembly macros in `nospec-insn.h`.

Risks and test signals: Mitigation policy must match hardware and compiler-generated call sequences. Tests should include boot with `nobp`/`nospec_disable` variants, facility-present/absent systems, objdump of thunk calls, and speculative mitigation selftests where available.
