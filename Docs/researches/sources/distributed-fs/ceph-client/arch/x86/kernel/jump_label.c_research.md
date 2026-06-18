# sources/distributed-fs/ceph-client/arch/x86/kernel/jump_label.c

Purpose: Provides x86 runtime patching for Linux static keys and jump labels. It switches compiled NOP sites to relative jumps, or back, using x86 text patching primitives.

Important APIs/types/functions: defines `arch_jump_entry_size()`, `arch_jump_label_transform()`, `arch_jump_label_transform_queue()`, and `arch_jump_label_transform_apply()`. Internal helper `__jump_label_patch()` validates the current instruction bytes and returns a `struct jump_label_patch` with replacement bytes and size.

Control flow: each jump entry identifies a code address and target. `arch_jump_entry_size()` decodes the instruction at the code address and accepts only 2-byte or 5-byte sites. `__jump_label_patch()` generates a short or near jump with `text_gen_insn()` or selects the matching x86 NOP sequence, then verifies the current bytes match the expected old state. Early boot and init transforms use `text_poke_early()`. Runtime single transforms use `smp_text_poke_single()`, while queued transforms add entries to the batch list and later flush them with `smp_text_poke_batch_finish()`.

State and persistence: no private persistent data is kept. State is encoded directly in kernel text as either an x86 NOP or JMP instruction. Batching state lives in the shared text-patching subsystem.

Dependencies and integration points: depends on `jump_entry` metadata emitted by the compiler/kernel, x86 instruction decoding, `x86_nops`, `text_mutex`, and SMP-safe text-poke APIs. It also respects boot state because text is still writable and single-CPU during early boot.

Risks: any byte mismatch is treated as fatal and triggers `BUG()` because it indicates text corruption or conflicting patchers. Instruction size assumptions must remain aligned with generated jump-label sites. Runtime callers must serialize through `text_mutex` to avoid races with other text patching such as alternatives, static calls, ftrace, or kprobes.

Test signals: static key selftests should toggle both 2-byte and 5-byte sites, exercise boot-time and runtime changes, and validate queued apply behavior. Fault-injection or debug builds should catch unexpected-byte detection if another patcher touches a site.
