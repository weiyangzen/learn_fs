# sources/distributed-fs/ceph-client/arch/x86/lib/atomic64_cx8_32.S

Purpose: implements 64-bit atomic operations for 586+ 32-bit x86 systems using `cmpxchg8b`, with lock-prefixed compare/exchange loops for SMP-safe updates.

Important APIs/functions: exports assembly entry points named `atomic64_read_cx8`, `atomic64_set_cx8`, `atomic64_xchg_cx8`, generated `atomic64_add_return_cx8`, `atomic64_sub_return_cx8`, `atomic64_inc_return_cx8`, `atomic64_dec_return_cx8`, plus `atomic64_dec_if_positive_cx8`, `atomic64_add_unless_cx8`, and `atomic64_inc_not_zero_cx8`. Helper macros `read64`, `read64_nonatomic`, `addsub_return`, and `incdec_return` encapsulate repeated patterns.

Control flow: operations read the current 64-bit value into `%edx:%eax`, compute a proposed new value in `%ecx:%ebx`, and use locked `cmpxchg8b` retry loops until the write succeeds or a conditional operation decides not to store. `atomic64_set_cx8` relies on aligned 64-bit writes being atomic on 586+ but still uses `cmpxchg8b` looping without lock. Conditional helpers return success in `%eax` or the decremented value as required by the atomic ABI.

State and persistence behavior: mutates only caller-provided atomic memory. No globals. Stack saves preserve callee-sensitive registers where loops need `%ebx`, `%esi`, `%edi`, and `%ebp`.

Dependencies/integration points: selected for 32-bit x86 with `CONFIG_X86_CX8` support. Coupled to the generic atomic64 wrapper and Linux x86 calling conventions.

Risks: correctness depends on alignment, exact register ABI, and proper lock prefix use. `read64` notes that `cmpxchg8b` writes even for read-like use, hence locked operation is required. Conditional comparisons in `add_unless` and zero checks are race-sensitive and must be looped.

Test signals: 32-bit SMP atomic stress tests, refcount-style `inc_not_zero` tests, signed `dec_if_positive` boundary tests, and build coverage for CX8-enabled CPUs.
