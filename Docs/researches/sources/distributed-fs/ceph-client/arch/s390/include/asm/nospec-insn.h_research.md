# sources/distributed-fs/ceph-client/arch/s390/include/asm/nospec-insn.h

Purpose: This assembly header defines expoline thunk generation and branch-site recording macros for s390 indirect branch mitigation.

Important APIs/types/functions: Under `CC_USING_EXPOLINE`, it defines thunk prolog/epilog macros, register decode helpers, `GEN_BR_THUNK`, `BR_EX`, and `BASR_EX`; without expoline it falls back to raw `br`/`basr`.

Control flow: Assembly code uses `BR_EX` or `BASR_EX` for indirect branches. In expoline builds, the macro emits a branch to the register-specific thunk and records the site offset in `.s390_indirect_branches` for later revert/patching.

State and persistence: Persistent state is generated thunk text, optional exported extern thunk symbols, and the `.s390_indirect_branches` metadata section.

Dependencies and integration points: It depends on assembler register syntax, linkage/export macros, DWARF CFI wrappers, compiler expoline configuration, and nospec branch runtime code.

Risks and test signals: Register decode macro errors or missing CFI can break assembly or unwinding. Tests should include assembler builds for all register variants, CONFIG_EXPOLINE_EXTERN on/off, module linkage to thunks, and runtime mitigation toggling.
