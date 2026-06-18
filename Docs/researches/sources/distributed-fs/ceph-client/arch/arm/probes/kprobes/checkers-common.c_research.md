<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c

Purpose: implements shared checker action decoders that classify stack space usage for ARM and Thumb kprobe safety checks.

Important functions: `checker_stack_use_none()` sets stack usage to 0. `checker_stack_use_unknown()` sets it to -1. Immediate helpers compute stack byte counts from instruction encodings: `checker_stack_use_imm_0xx()` for Thumb imm8, `checker_stack_use_t32strd()` for Thumb32 STRD imm8 scaled by 4, `checker_stack_use_imm_x0x()` for ARM split halfword immediates when Thumb2 is not configured, and `checker_stack_use_imm_xxx()` for ARM imm12. `checker_stack_use_stmdx()` derives stack cost from register-list population and pre/post indexing.

Control flow: architecture-specific stack checkers decode a suspicious store form to one of the `STACK_USE_*` action IDs; `stack_check_actions[]` maps that ID to these functions. The functions return `INSN_GOOD_NO_SLOT` because no executable instruction slot is needed for metadata-only classification.

State and persistence: no persistent state. It writes `asi->stack_space`, where negative means statically unknown and positive means extra bytes of stack below SP that must be protected.

Dependencies and integration: depends on `decode.h`, ARM decode definitions, and `checkers.h`; selected helper availability is conditional on `CONFIG_THUMB2_KERNEL`.

Risks: immediate extraction differs across ARM, T16, and T32 encodings. A wrong scale for STRD or incorrect STMDB pre/post adjustment changes whether `arch_prepare_kprobe()` accepts unsafe stack stores. Returning metadata-only success must not be confused with an executable action.

Test signals: both ARM and Thumb tests include fixed negative SP stores at and beyond `MAX_STACK_SIZE`, register-indexed SP stores expected to be rejected as unknown, and push/STMDB forms whose stack byte count is register-list dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-common.c -->
