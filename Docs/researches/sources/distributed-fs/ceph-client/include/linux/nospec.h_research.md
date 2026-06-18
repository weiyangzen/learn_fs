# sources/distributed-fs/ceph-client/include/linux/nospec.h

Purpose: Declares speculation barrier helpers for array-index masking and task speculation-control plumbing.

Important APIs, types, and functions: Exports `array_index_mask_nospec()`, `array_index_nospec()`, `arch_prctl_spec_ctrl_get()`, `arch_prctl_spec_ctrl_set()`, and `arch_seccomp_spec_mitigate()`. Detected source surface: 74 lines; includes `asm/barrier.h`, `linux/compiler.h`; macros `_LINUX_NOSPEC_H`, `array_index_nospec`, `barrier_nospec`; structs `task_struct`; enums none; typedefs none; function-like declarations/helpers `arch_prctl_spec_ctrl_get`, `arch_prctl_spec_ctrl_set`, `arch_seccomp_spec_mitigate`, `array_index_mask_nospec`.

Control flow: Callers pass an index and size through `array_index_nospec()` after bounds checks; the helper masks out-of-range indexes under speculative execution and emits architecture barriers through included asm support.

State and persistence behavior: No local state is defined. Speculation control state is task/architecture state managed by implementation files.

Dependencies and integration points: Depends on compiler annotations and architecture barrier primitives. Used by syscall, BPF, array lookup, and seccomp/speculation mitigation code.

Risks and test signals: Risks are using the helper before a real bounds check, wrong integer types causing truncation, and arch stub weakness. Test with static analysis for Spectre-v1 patterns, bounds-check call sites, and architecture mitigation selftests.
