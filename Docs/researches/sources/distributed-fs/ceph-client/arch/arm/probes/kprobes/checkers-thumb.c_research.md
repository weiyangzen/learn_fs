<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c

Purpose: provides Thumb-specific stack checkers for T32 load/store families and T16 push instructions.

Important functions: `t32_check_stack()` contains a nested decode table that first ignores all loads, marks register-indexed stores involving SP as unknown, computes fixed stack use for negative SP immediate stores, handles T32 STRD scaling, handles STMDB register-list stack use, and defaults to no stack use. `t16_check_stack()` computes push stack space as `hweight32(reglist) * 4`.

Control flow: `t32_stack_checker[]` attaches `t32_check_stack()` to T32 LDM/STM, LDRD/STRD, and LDR/STR actions. `t16_stack_checker[]` attaches `t16_check_stack()` only to `PROBES_T16_PUSH`, reflecting that other 16-bit Thumb stack-relevant stores cannot address below SP in the same dangerous way.

State and persistence: no global state. Writes `asi->stack_space`, which `arch_prepare_kprobe()` later bounds against `MAX_STACK_SIZE`.

Dependencies and integration: depends on `decode-thumb.h`, shared `stack_check_actions`, and `checkers.h`. Used only in Thumb2 kernels through `kprobes_t32_checkers` and `kprobes_t16_checkers`.

Risks: T32 register-store encodings include invalid patterns intentionally used to simplify masks; changes to decode tables need matching checker masks. T16 stack classification assumes only push can require extra protected stack space, so adding new T16 store actions requires reassessment.

Test signals: `test-thumb.c` includes push register lists, T32 STR/STRB/STRH/STRD negative SP stores, register-offset SP stores expected to be unsupported, and boundary cases around `MAX_STACK_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-thumb.c -->
