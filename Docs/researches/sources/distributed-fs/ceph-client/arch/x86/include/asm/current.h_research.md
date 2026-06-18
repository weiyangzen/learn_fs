
# sources/distributed-fs/ceph-client/arch/x86/include/asm/current.h

Purpose: x86 implementation of the `current` task accessor.

Important APIs and control flow: declares cache-hot per-CPU `current_task` and a const per-CPU segment override alias `const_current_task`. `get_current()` reads `const_current_task` through segment support when enabled, otherwise uses stable per-CPU read of `current_task`. The macro `current` maps to `get_current()`.

State, dependencies, and risks: state is per-CPU current task pointer. Dependencies include x86 percpu access mode, linker-provided alias, and scheduler context switching. Risks include wrong per-CPU segment setup, stale current pointer during entry/exit transitions, and assumptions about const alias availability. Test signals are scheduler/context switch tests, entry code, and percpu access build variants.
