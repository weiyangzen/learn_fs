
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cmpxchg_32.h

Purpose: 32-bit x86 64-bit compare-exchange support.

Important APIs and control flow: `union __u64_halves` splits 64-bit values into low/high words for `cmpxchg8b`. Native `__cmpxchg64` and `__try_cmpxchg64` use locked or local `cmpxchg8b`. With `CONFIG_X86_CX8`, public macros alias directly. Without it, `arch_cmpxchg64*` and `arch_try_cmpxchg64*` use alternatives to call `cmpxchg8b_emu` on old CPUs or use real `cmpxchg8b` when available.

State, dependencies, and risks: state is 64-bit memory accessed from 32-bit code. Dependencies include CX8 detection, `cmpxchg8b_emu`, and correct register splitting. Risks include using qword atomics before feature alternatives are usable, emulation correctness on 386/486, and alignment requirements. Test signals are 32-bit atomic64 tests and non-CX8 build/runtime coverage.
