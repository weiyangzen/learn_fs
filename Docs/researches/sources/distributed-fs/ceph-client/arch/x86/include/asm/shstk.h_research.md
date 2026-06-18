<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h

Purpose: declares x86 user shadow stack state and control hooks for Intel CET. Important type is `thread_shstk`; important APIs include `shstk_setup()`, `shstk_alloc_thread_stack()`, `shstk_free()`, `shstk_disable()`, `reset_thread_features()`, and arch-prctl feature locking helpers, with stubs when shadow stacks are disabled.

Control flow: exec/thread creation allocates and initializes user shadow stacks; arch-prctl and signal paths enable, disable, or lock features; exit/exec frees state. State is per-thread shadow-stack address/size and feature masks in `thread_struct`.

Dependencies include CET CPU features, memory management, arch-prctl, signal delivery, and `thread_struct` feature fields. Risks include leaking shadow-stack mappings, wrong feature-lock semantics, signal restore mismatches, and ABI regressions. Test signals include CET/shstk selftests, clone/exec/exit, arch_prctl enable/disable/lock, signal delivery, and non-CET stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shstk.h -->
