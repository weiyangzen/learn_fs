# sources/distributed-fs/ceph-client/arch/arm/kernel/jump_label.c

Purpose: implements ARM static key/jump label patching by replacing NOPs with generated branches or restoring NOPs.

Important APIs/types/functions: `arch_jump_label_transform` is the runtime entry; `__arch_jump_label_transform` handles both early and live patching. It uses `arm_gen_branch`, `arm_gen_nop`, `__patch_text_early`, and `patch_text`.

Control flow: for each `jump_entry`, the requested type selects branch-to-target or NOP. Early static transformations write directly; live transformations use synchronized text patching.

State and persistence: modified kernel text is persistent until the static key changes again. No local state is kept.

Dependencies and integration: depends on jump label core metadata, instruction generation, and ARM text patching.

Risks: branch range and Thumb/ARM encoding must be correct; live patching must synchronize I-cache and CPUs. Test signals include static key selftests, boot-time static key initialization, and live enable/disable under SMP.
