<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h

Purpose: declares the checker action interface and stack-use classification IDs shared by ARM and Thumb kprobe checker implementations.

Important APIs and types: exports `checker_stack_use_none`, `checker_stack_use_unknown`, immediate stack-use helpers selected by `CONFIG_THUMB2_KERNEL`, `checker_stack_use_imm_xxx`, and `checker_stack_use_stmdx`. Defines the `STACK_USE_*` enum used as action indexes into `stack_check_actions[]`. Declares checker arrays for ARM (`arm_stack_checker`, `arm_regs_checker`) on non-Thumb2 builds and Thumb (`t32_stack_checker`, `t16_stack_checker`) generally.

Control flow: architecture-specific checker tables use action IDs from this header when their nested decode tables classify an instruction. The shared decoder treats these actions as custom decoders, so the checker function updates `struct arch_probes_insn` metadata and returns an `enum probes_insn`.

State and persistence: no state in the header. It defines how checker code writes stack/register metadata into `arch_probes_insn`.

Dependencies and integration: includes `decode.h` for `probes_check_t`, `union decode_action`, and `struct decode_checker`. Used by all `actions-*` files to expose checker arrays consumed by `core.c`.

Risks: enum ordering must stay synchronized with `stack_check_actions[]` in `checkers-common.c` and with decode-table action IDs in checker tables. Conditional enum members differ between Thumb2 and ARM builds, so cross-ISA assumptions about numeric values are unsafe.

Test signals: compile coverage across Thumb2 and non-Thumb2 builds is important because different declarations and enum members are active. Runtime tests validate the stack metadata produced through these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers.h -->
