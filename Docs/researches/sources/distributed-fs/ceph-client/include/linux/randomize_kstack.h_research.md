# sources/distributed-fs/ceph-client/include/linux/randomize_kstack.h

Purpose: implements the architecture-agnostic macro used by syscall entry paths to add a bounded random stack offset for stack-layout hardening when `CONFIG_RANDOMIZE_KSTACK_OFFSET` is enabled.

Important APIs and types: `randomize_kstack_offset` is a static key controlling enablement. `__kstack_alloca` selects uninitialized alloca when supported. `KSTACK_OFFSET_MAX()` masks random values to a bounded, alignment-friendly range. `DECLARE_PER_CPU(struct rnd_state, kstack_rnd_state)` stores per-CPU PRNG state. `get_kstack_offset()` samples per-CPU random state, and `add_random_kstack_offset()` performs the stack allocation and compiler barrier.

Control flow: syscall entry invokes `add_random_kstack_offset()` after user registers are stored. If the static branch is enabled, it samples a per-CPU PRNG value, masks it to the maximum offset, allocates that much stack with alloca, and uses inline asm to keep the allocation live.

State and persistence: runtime state is per-CPU pseudo-random state and the static-key enable flag. No persistent data is stored.

Dependencies and integration points: depends on jump labels, percpu definitions, `prandom`, compiler builtins, stack initialization behavior, and syscall entry architecture code.

Risks and test signals: risks include excessive stack use, compiler optimizing away the allocation, unwanted stack zeroing overhead, use in unsafe noinstr contexts, per-CPU PRNG quality, and architecture alignment mismatches. Test enabled/disabled configs, runtime static-key toggling, LKDTM stack entropy selftest, syscall stress under small stacks, and GCC/Clang code generation.
