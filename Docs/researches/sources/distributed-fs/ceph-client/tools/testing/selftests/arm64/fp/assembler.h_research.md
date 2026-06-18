# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/assembler.h

Purpose: macro library for arm64 FP/SVE/SME assembly tests.

Important APIs/types/functions: recursive `_for`/`__for` macros generate repeated code; `function`/`endfunction` annotate functions; `define_accessor` builds indexed accessor jump tables; `puts` macro emits literal strings and calls runtime `puts`; GCS constants and `enable_gcs` macro issue `prctl(PR_SET_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE)`.

Control flow: all behavior is assembly-time macro expansion except `enable_gcs`, which emits runtime syscall instructions.

State and persistence: may emit string constants into `.rodata`; no persistent state.

Dependencies/integration: included by arm64 FP assembly sources and `asm-utils.S`.

Risks and test signals: recursive macro expansion can stress assembler limits for large ranges. `enable_gcs` assumes current kernel supports the prctl numbers and shadow-stack semantics.
