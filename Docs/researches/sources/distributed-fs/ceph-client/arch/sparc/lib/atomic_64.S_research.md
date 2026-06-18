# sources/distributed-fs/ceph-client/arch/sparc/lib/atomic_64.S

Purpose: SPARC64 atomic integer and atomic64 operations using compare-and-swap loops.

Important APIs/functions: Exports `arch_atomic_{add,sub,and,or,xor}`, return/fetch variants, `arch_atomic64_*` equivalents, and `arch_atomic64_dec_if_positive`.

Control flow: Macros generate loops that load current value, compute new value, attempt `cas`/`casx`, and retry with `BACKOFF_SPIN` on contention. Return variants return new value; fetch variants return old value. `dec_if_positive` decrements only if the old value is nonnegative after decrement semantics allow it.

State and persistence: Mutates atomic memory locations; no separate state.

Dependencies/integration: Includes `asm/asi.h` and `asm/backoff.h`; built for `CONFIG_SPARC64`.

Risks/test signals: Memory ordering, retry loops, and signed dec-if-positive behavior are critical. Run atomic selftests, concurrency stress, and compare return/fetch semantics.
