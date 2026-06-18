# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_atomic.h

Purpose: provides kernel-like atomic and memory-ordering helper macros for BPF programs used by selftests.

Important APIs and macros: `READ_ONCE`, `WRITE_ONCE`, `cmpxchg`, `try_cmpxchg*`, `smp_mb/rmb/wmb`, `smp_load_acquire`, `smp_store_release`, `smp_cond_load_*_label`, `atomic_read`, `atomic_cond_read_*`, and `atomic_try_cmpxchg_*`. `__unqual_typeof()` strips scalar qualifiers while preserving pointer behavior around an LLVM address-space issue.

Control flow: macros expand into volatile accesses, compiler barriers, and `__sync_*` builtins. X86 uses weaker barrier paths for rmb/wmb/load/store where appropriate; other architectures fall back to full memory barriers.

State and persistence: no runtime state except accessed atomic variables.

Dependencies and integration points: includes `vmlinux.h`, BPF helpers, `bpf_experimental.h`, and weak kconfig `CONFIG_X86_64`.

Risks: macro-heavy code is type-sensitive; behavior depends on target architecture config; full barriers may be more expensive on non-x86; misuse on non-atomic struct layout can fail verification or produce races.

Test signals: atomic selftests should compile and validate compare-exchange success/failure, acquire/release ordering, and conditional load loop behavior.
