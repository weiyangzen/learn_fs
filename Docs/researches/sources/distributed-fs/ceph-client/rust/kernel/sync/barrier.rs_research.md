## sources/distributed-fs/ceph-client/rust/kernel/sync/barrier.rs

Purpose: exposes compiler and SMP memory barriers matching Linux Kernel Memory Model semantics.

Important APIs/types/functions: private `barrier()` emits an empty inline asm block as a compiler barrier. Public `smp_mb`, `smp_wmb`, and `smp_rmb` call the matching C bindings on SMP builds or fall back to the compiler barrier on non-SMP builds.

Control flow: each public function checks `cfg!(CONFIG_SMP)` at compile time and chooses the C barrier or compiler-only fallback.

State/persistence: no state.

Dependencies/integration: depends on `core::arch::asm!` and barrier C bindings. Used by synchronization code that needs explicit LKMM barriers outside typed atomics.

Risks: barriers are low-level and do not provide mutual exclusion or lifetime management. Incorrect placement can leave races even when barriers are present. The empty asm relies on Rust inline-asm memory effects being conservative enough for compiler reordering prevention.

Test signals: no local tests. Validation comes from architecture build coverage and LKMM/litmus reasoning in users.
