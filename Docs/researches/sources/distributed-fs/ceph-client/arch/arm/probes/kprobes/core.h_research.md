<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h

Purpose: declares ARM kprobe-private constants and cross-file interfaces for breakpoint encodings, breakpoint removal, LDM/STM decode, ISA-specific action/checker tables, and the decode-function signature used by core preparation.

Important APIs and types: defines `KPROBE_ARM_BREAKPOINT_INSTRUCTION`, `KPROBE_THUMB16_BREAKPOINT_INSTRUCTION`, and `KPROBE_THUMB32_BREAKPOINT_INSTRUCTION`. Declares `kprobes_remove_breakpoint()`, `kprobe_decode_ldmstm()`, and `typedef kprobe_decode_insn_t`. Exposes `kprobes_t32_actions`, `kprobes_t16_actions`, `kprobes_t32_checkers`, and `kprobes_t16_checkers` for Thumb2, or `kprobes_arm_actions` and `kprobes_arm_checkers` for ARM mode.

Control flow: `core.c` includes this header to select the appropriate decode/action/checker arrays in `arch_prepare_kprobe()`. `actions-common.c` exports the LDM/STM custom decoder declared here.

State and persistence: no state; the constants define the persistent breakpoint instruction values that get patched into kernel text while probes are armed.

Dependencies and integration: includes `asm/kprobes.h` and shared `decode.h`. It is the narrow coupling layer between core probe management and action/checker implementations.

Risks: breakpoint encodings must remain unique and reserved for kprobes undefined-instruction hooks. A mismatch between declarations and Makefile-selected objects will cause link failures or runtime decode table misuse. The decode-function typedef must match ARM/Thumb decode wrapper signatures.

Test signals: build and boot-time kprobe tests indirectly validate that the right arrays are linked and that breakpoint values trap through the registered undefined hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.h -->
