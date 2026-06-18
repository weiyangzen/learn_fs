## sources/distributed-fs/beegfs/client_module/source/os/atomic64.c

**Purpose:** Supplies a fallback generic 64-bit atomic implementation for kernels/architectures that do not provide `atomic64_t`.

**Important APIs/types/functions:** When `ATOMIC64_INIT` is absent, implements `atomic64_read`, `atomic64_set`, `atomic64_add`, `atomic64_add_return`, `atomic64_sub`, `atomic64_sub_return`, `atomic64_dec_if_positive`, `atomic64_cmpxchg`, `atomic64_xchg`, and `atomic64_add_unless`.

**Control flow:** Each operation obtains the per-object spinlock from `lock_addr`, disables interrupts with `spin_lock_irqsave`, reads/modifies `counter`, and unlocks with saved flags. The BeeGFS version uses a lock embedded in each `atomic64_t` rather than the upstream hashed lock table.

**State and persistence behavior:** State lives in each fallback `atomic64_t` as a `long long counter` plus `spinlock_t lock`. No global state is used in the active BeeGFS fallback path.

**Dependencies and integration points:** Included only on kernels lacking native atomic64 support. The companion header defines the fallback type and `atomic_init`. Any BeeGFS code using atomic64 APIs relies on either native kernel definitions or these functions.

**Risks:** The fallback is slower than native atomic instructions and depends on every object being initialized with `atomic_init` so the embedded spinlock is valid. Because it is conditionally compiled, build coverage on modern kernels will not exercise it.

**Test signals:** Build on a configuration without `ATOMIC64_INIT`, run concurrent increment/decrement/cmpxchg/add-unless tests, verify interrupt-safe locking under lockdep, and ensure all fallback atomic64 objects are initialized before use.
