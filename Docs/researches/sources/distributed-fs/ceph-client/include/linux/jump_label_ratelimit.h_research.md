# sources/distributed-fs/ceph-client/include/linux/jump_label_ratelimit.h

## Purpose
Extends static keys with deferred decrement support so user-controlled or high-frequency toggles do not repeatedly patch code. It rate-limits the expensive false transition by scheduling delayed work.

## Important APIs, Types, And Functions
With `CONFIG_JUMP_LABEL`, it defines `struct static_key_deferred`, `struct static_key_true_deferred`, and `struct static_key_false_deferred`, each carrying a key, timeout, and `delayed_work`. Macros include `DEFINE_STATIC_KEY_DEFERRED_TRUE/FALSE`, `static_key_slow_dec_deferred()`, `static_branch_slow_dec_deferred()`, `static_key_deferred_flush()`, and `static_branch_deferred_inc()`.

## Control Flow
Increment paths immediately increase the underlying key. Decrement paths call `__static_key_slow_dec_deferred()` with the delayed work and timeout; the work function later performs the update. Flush paths force pending work completion. Without jump labels, deferred structures shrink to just the typed key and decrement becomes a direct `static_branch_dec()`.

## State And Persistence
Runtime state is the key count plus pending delayed work and timeout. It is not persistent and must be flushed before teardown when users need a deterministic final key state.

## Dependencies And Integration Points
Depends on `linux/jump_label.h` and `linux/workqueue.h`. Integrates with subsystems that expose static branch controls to userspace or other potentially bursty sources.

## Risks
Forgetting to flush during teardown can leave delayed work referencing dead storage. Deferred decrements mean the observed static branch state can remain enabled temporarily after the last user releases it. Fallback builds do not rate-limit because no text patching is involved.

## Test Signals
Tests should cover bursty inc/dec behavior, timeout expiry, flush before module unload, fallback builds without `CONFIG_JUMP_LABEL`, and races between a deferred decrement and a new increment.
