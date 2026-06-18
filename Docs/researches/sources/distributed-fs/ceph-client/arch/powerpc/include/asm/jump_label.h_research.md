# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/jump_label.h

Purpose: Implements PowerPC static key/jump-label architecture support for patching conditional branches at runtime.

Important APIs, types, and functions: Defines architecture jump-label instruction layout and helpers for emitting/evaluating branch or NOP sequences. It integrates with `arch_static_branch()` and `arch_static_branch_jump()` style static-key calls.

Control flow: Static key sites compile to patchable branch/NOP instructions. Runtime key changes patch the instruction stream so hot paths avoid a memory load when the key is disabled or enabled.

State and persistence: Static key state lives in generic jump-label structures and patched kernel text. No independent persistent state.

Dependencies and integration points: Depends on PowerPC branch encodings, text patching, and generic jump-label infrastructure.

Risks: Branch displacement and instruction cache synchronization are critical. Patching must be atomic enough for running CPUs. Incorrect sense of default branch can invert static key behavior.

Test signals: Static key enable/disable stress, module jump labels, SMP patching while executing, branch range tests, and objdump verification of generated sites.
